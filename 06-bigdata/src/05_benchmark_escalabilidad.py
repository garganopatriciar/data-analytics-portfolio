"""Evaluación de rendimiento y escalabilidad.
Replica el dataset armonizado x1, x4, x16 (≈1,2 M a ≈19 M registros) y mide
la misma consulta (egresos ICSAP por año y región) en:
  - pandas (un proceso, todo en memoria)
  - Spark local[1] y local[2] sobre CSV
  - Spark local[2] sobre Parquet
Cada corrida se ejecuta en un subproceso aislado para medir tiempo y memoria pico.
"""
import json, os, subprocess, sys, time, shutil
from common import spark_session, SILVER, BASE, OUT

BENCH = os.path.join(BASE, "data", "bench")
FACTORES = [1, 4, 16]
RX = ("^ASMA$|BRONQUITIS, ENFISEMA|CRONICAS DE LAS VIAS RESPIRATORIAS INFERIORES|^DIABETES|HIPERTENSIVAS|"
      "INFECCIOSAS INTESTINALES|PREVENIBLES POR VACUNAS|SARAMPION|TOS FERINA|PAROTIDITIS|VARICELA|"
      "^TUBERCULOSIS|^DESNUTRICION|^EPILEPSIA")


def preparar():
    from pyspark.sql import functions as F
    spark = spark_session("bench-prep")
    s = spark.read.parquet(SILVER)
    tam = {}
    for f in FACTORES:
        rep = s.crossJoin(spark.range(f).withColumnRenamed("id", "replica"))
        for fmt in ("csv", "parquet"):
            p = os.path.join(BENCH, f"x{f}_{fmt}")
            w = rep.repartition(8).write.mode("overwrite")
            (w.option("header", True).csv(p) if fmt == "csv" else w.parquet(p))
            tam[f"x{f}_{fmt}_MB"] = round(sum(os.path.getsize(os.path.join(dp, fn))
                                             for dp, _, fns in os.walk(p) for fn in fns) / 1e6, 1)
        tam[f"x{f}_filas"] = s.count() * f
    spark.stop()
    return tam


def run_pandas(f):
    import glob, pandas as pd, re
    t = time.time()
    files = glob.glob(os.path.join(BENCH, f"x{f}_csv", "*.csv"))
    df = pd.concat((pd.read_csv(x, usecols=["anio", "region_sanitaria", "causa", "cantidad"],
                                dtype={"causa": "category", "region_sanitaria": "category"}) for x in files),
                   ignore_index=True)
    mask = df["causa"].astype(str).str.contains(RX, regex=True)
    res = df[mask].groupby(["anio", "region_sanitaria"], observed=True)["cantidad"].sum()
    return time.time() - t, int(res.sum())


def run_spark(f, cores, fmt):
    from pyspark.sql import functions as F
    spark = spark_session(f"bench-{fmt}-{cores}", cores=cores)
    t = time.time()
    p = os.path.join(BENCH, f"x{f}_{fmt}")
    df = spark.read.option("header", True).option("inferSchema", False).csv(p) if fmt == "csv" else spark.read.parquet(p)
    res = (df.filter(F.col("causa").rlike(RX)).groupBy("anio", "region_sanitaria")
             .agg(F.sum(F.col("cantidad").cast("long")).alias("q")))
    total = res.agg(F.sum("q")).first()[0]
    el = time.time() - t
    spark.stop()
    return el, int(total)


if __name__ == "__main__":
    if len(sys.argv) > 1:   # modo worker
        motor, f = sys.argv[1], int(sys.argv[2])
        if motor == "pandas":
            el, tot = run_pandas(f)
        else:
            _, cores, fmt = motor.split("_")
            el, tot = run_spark(f, int(cores), fmt)
        import resource
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024  # MB (proceso python/driver)
        print(json.dumps({"seg": round(el, 2), "total": tot, "rss_mb": round(rss)}))
        sys.exit(0)

    tam = preparar()
    filas = []
    for f in FACTORES:
        for motor in ["pandas", "spark_1_csv", "spark_2_csv", "spark_2_parquet"]:
            out = subprocess.run([sys.executable, __file__, motor, str(f)], capture_output=True, text=True)
            line = [l for l in out.stdout.splitlines() if l.startswith("{")]
            r = json.loads(line[-1]) if line else {"error": out.stderr[-400:]}
            r.update({"factor": f, "motor": motor, "filas": tam[f"x{f}_filas"]})
            print(r, flush=True)
            filas.append(r)
    with open(os.path.join(OUT, "benchmark.json"), "w") as fh:
        json.dump({"tamanios": tam, "corridas": filas}, fh, indent=2)
    print(json.dumps(tam, indent=2))
