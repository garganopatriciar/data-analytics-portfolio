# 06 · Big Data — Internaciones evitables en el sistema público de la PBA

**Trabajo Final Integrador · Análisis de Datos Masivos · Lic. en Ciencias de Datos (UCASAL, 2026)**  
Autora: Patricia Gargano · Docente: Prof. Gustavo Ramiro Rivadera  
Informe: [`informe/TFI_ADM2026_Informe.pdf`](informe/TFI_ADM2026_Informe.pdf)

Pipeline Big Data (arquitectura medallion bronze/silver/gold) sobre los egresos hospitalarios
públicos de la Provincia de Buenos Aires 2016-2022, para cuantificar las Internaciones por
Condiciones Sensibles al cuidado Ambulatorio (ICSAP) y priorizar territorios para telemedicina/APS.

## Cómo evaluar este trabajo

**Opción 1 — Sin ejecutar nada.** Los resultados ya están en `outputs/` (tablas CSV, JSON de calidad,
benchmark y validación MapReduce) y las figuras en `outputs/figuras/`. El informe está en `informe/`.

**Opción 2 — Google Colab (recomendada, no requiere instalar nada).**
Abrir https://colab.research.google.com > Notebook nuevo y ejecutar en una celda:
```
!git clone -q https://github.com/garganopatriciar/data-analytics-portfolio.git
%cd data-analytics-portfolio/06-bigdata
!pip install -q -r requirements.txt
!bash run_all.sh rapido
```
(`rapido` omite el benchmark de escalabilidad; sin ese argumento corre todo, ~10 min.)

**Opción 3 — Computadora propia** (Linux, macOS o Windows con WSL; Python 3.10+ y Java 17/21):
```
git clone https://github.com/garganopatriciar/data-analytics-portfolio.git
cd data-analytics-portfolio/06-bigdata
pip install -r requirements.txt
bash run_all.sh rapido
```

Los datos originales se incluyen comprimidos en `data/raw/egresos_raw.zip` (con sus checksums SHA-256);
`00_descarga.sh` los descomprime y verifica. Si faltaran, los vuelve a bajar del portal oficial.

## Requisitos
- Linux, macOS o Windows con WSL. Python 3.10+ y Java 17/21 · `pip install -r requirements.txt`
- Probado con Python 3.13, OpenJDK 21 y pyspark 3.5.3 y 4.0.5 (mismos resultados)
- ~5 GB libres en disco si se corre el benchmark (x16)

## Reproducir
```bash
bash run_all.sh            # todo el flujo (≈10 min en 2 núcleos); 'rapido' omite el benchmark
```
o paso a paso:

| Script | Etapa | Salida |
|---|---|---|
| `src/00_descarga.sh` | Adquisición (bronze) | `data/raw/*.csv` (desde el zip o el portal) + verificación de checksums |
| `src/01_ingesta_silver.py` | Armonización, calidad, Parquet particionado | `data/silver/`, `outputs/calidad_ingesta.json` |
| `src/02_gold_analisis.py` | Spark SQL, ventanas, ICSAP, estandarización por edad | `data/gold/`, `outputs/gold_*.csv` |
| `src/03_mapreduce/run_local.sh` | MapReduce estilo Hadoop Streaming (map→shuffle/sort→reduce) | `outputs/mapreduce_resultado.tsv` |
| `src/03_mapreduce/rdd_spark.py` | MapReduce sobre RDD + validación cruzada | consola |
| `src/04_clustering_mllib.py` | K-Means (MLlib) de municipios | `outputs/clusters_*.csv/json` |
| `src/05_benchmark_escalabilidad.py` | pandas vs Spark, CSV vs Parquet, 1 vs 2 núcleos | `outputs/benchmark.json` |
| `src/06_figuras.py` | Figuras | `outputs/figuras/` |

En un clúster Hadoop, el paso 03 se ejecuta con:
```
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -files mapper.py,reducer.py -mapper mapper.py -reducer reducer.py \
  -input /raw/egresos/*.csv -output /out/icsap_mr
```

## Datos
Ministerio de Salud de la Provincia de Buenos Aires — *Egresos hospitalarios*, Portal de Datos Abiertos PBA:
https://catalogo.datos.gba.gob.ar/dataset/egresos-hospitalarios (licencia abierta). Datos agregados, sin información personal.

## Estructura
```
06-bigdata/
├── README.md · requirements.txt · run_all.sh
├── data/raw/          # capa bronze: egresos_raw.zip + checksums.sha256
├── src/               # 00-06: pipeline (Spark, MapReduce, MLlib, benchmark, figuras)
├── outputs/           # resultados (CSV/JSON) y figuras generadas
└── informe/           # informe PDF y su fuente HTML
```
