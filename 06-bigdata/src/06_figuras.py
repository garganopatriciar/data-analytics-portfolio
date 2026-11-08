"""Genera las figuras del informe a partir de las tablas gold (CSV en outputs/)."""
import json, os
import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
O = os.path.join(BASE, "outputs"); FIG = os.path.join(O, "figuras"); os.makedirs(FIG, exist_ok=True)
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e6e5e0"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": GRID,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
                     "axes.titlesize": 10, "axes.titleweight": "bold", "axes.titlecolor": INK,
                     "legend.frameon": False, "savefig.dpi": 200, "savefig.bbox": "tight"})

# ---- Fig 2: serie anual (dos paneles, un eje cada uno) ----
a = pd.read_csv(f"{O}/gold_anual.csv")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3.2))
ax1.bar(a.anio, a.egresos / 1e3, color=CAT[0], width=0.6, label="Egresos totales")
ax1.bar(a.anio, a.egresos_covid / 1e3, color=CAT[1], width=0.6, label="de ellos COVID-19")
ax1.set_title("Egresos hospitalarios por año (miles)"); ax1.legend(loc="upper left", fontsize=8)
for x, y in zip(a.anio, a.egresos / 1e3):
    ax1.text(x, y + 15, f"{y:,.0f}".replace(",", "."), ha="center", fontsize=7, color=INK2)
ax1.set_ylim(0, 1300)
for col, c, lab in [("pct_icsap_ampliado", CAT[1], "ICSAP ampliado"), ("pct_icsap_estricto", CAT[0], "ICSAP estricto")]:
    ax2.plot(a.anio, a[col], color=c, lw=2, marker="o", ms=5, label=lab)
    ax2.text(a.anio.iloc[-1] + 0.15, a[col].iloc[-1], f"{a[col].iloc[-1]:.1f}%", va="center", fontsize=8, color=INK)
ax2.axvspan(2019.5, 2021.5, color="#f1f0ec", zorder=0); ax2.text(2020.5, 22.3, "pandemia", ha="center", fontsize=7, color=INK2)
ax2.set_ylim(0, 24); ax2.set_title("% de egresos no obstétricos que son ICSAP"); ax2.legend(loc="lower left", fontsize=8)
ax2.set_xlim(2015.6, 2022.9)
fig.savefig(f"{FIG}/fig2_serie_anual.png"); plt.close(fig)

# ---- Fig 3: heatmap edad x condición ----
e = pd.read_csv(f"{O}/gold_edad_condicion.csv")
e = e[e.grupo_edad != "IGN"]
piv = e.pivot_table(index="icsap_condicion", columns="grupo_edad", values="pct_sobre_edad", aggfunc="sum").fillna(0)
piv = piv.loc[piv.sum(axis=1).sort_values(ascending=False).index]
cmap = LinearSegmentedColormap.from_list("seq", ["#f4f8fd", "#a9c8ef", "#2a78d6", "#123f78"])
fig, ax = plt.subplots(figsize=(9, 3.9))
im = ax.imshow(piv.values, aspect="auto", cmap=cmap)
ax.set_xticks(range(len(piv.columns)), piv.columns, rotation=45, ha="right")
ax.set_yticks(range(len(piv.index)), piv.index); ax.grid(False)
for i in range(piv.shape[0]):
    for j in range(piv.shape[1]):
        v = piv.values[i, j]
        if v >= 3:
            ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=6.5, color="white" if v > 9 else INK)
cb = fig.colorbar(im, ax=ax, fraction=0.025); cb.set_label("% de egresos no obstétricos del grupo de edad")
ax.set_title("Peso de cada condición ICSAP según grupo de edad (2016-2022)")
fig.savefig(f"{FIG}/fig3_heatmap_edad.png"); plt.close(fig)

# ---- Fig 4: condiciones estrictas por año (índice 2019 = 100) ----
c = pd.read_csv(f"{O}/gold_condicion_anio.csv")
top = ["Hipertension", "Gastroenteritis", "Asma", "Diabetes", "EPOC"]
fig, ax = plt.subplots(figsize=(9, 3.2)); ends = []
for i, k in enumerate(top):
    s = c[c.icsap_condicion == k].set_index("anio").egresos.sort_index()
    idx = 100 * s / s.loc[2019]
    ax.plot(idx.index, idx.values, color=CAT[i], lw=2, marker="o", ms=4, label=k)
    ends.append([idx.loc[2022], f"{k} {idx.loc[2022]:.0f}"])
ends.sort(key=lambda e: e[0]); 
for i in range(1, len(ends)):
    ends[i][0] = max(ends[i][0], ends[i-1][0] + 7)
for y, t in ends:
    ax.text(2022.15, y, t, va="center", fontsize=7.5, color=INK)
ax.axhline(100, color=INK2, lw=0.8, ls="--"); ax.set_xlim(2015.7, 2023.3); ax.set_xticks(range(2016, 2023))
ax.set_title("Internaciones por condición ICSAP crónica/aguda (índice 2019 = 100)")
ax.legend(ncol=5, loc="upper left", fontsize=8)
fig.savefig(f"{FIG}/fig4_indice_condiciones.png"); plt.close(fig)

# ---- Fig 5: municipios — %65+ vs razón O/E, por clúster ----
m = pd.read_csv(f"{O}/clusters_municipios.csv"); cs = pd.read_csv(f"{O}/clusters_resumen.csv")
nombres = {0: "C0 urbano joven", 1: "C1 cardiometabólico", 2: "C2 brecha ambulatoria", 3: "C3 envejecido, baja ICSAP"}
fig, ax = plt.subplots(figsize=(9, 3.8))
for k in sorted(m.cluster.unique()):
    d = m[m.cluster == k]
    ax.scatter(d.pct_65mas, d.razon_oe, s=np.clip(d.egresos / 2500, 12, 260), color=CAT[k], alpha=0.75,
               edgecolor="white", linewidth=1, label=nombres.get(k, f"C{k}"))
ax.axhline(1, color=INK2, lw=0.8, ls="--")
for _, r in m.sort_values("razon_oe", ascending=False).head(6).iterrows():
    ax.annotate(r.municipio.title(), (r.pct_65mas, r.razon_oe), xytext=(4, 3), textcoords="offset points", fontsize=7, color=INK)
ax.set_xlabel("% de egresos no obstétricos de personas de 65 años o más")
ax.set_ylabel("Razón ICSAP observada/esperada")
ax.set_title("Municipios de PBA: razón ICSAP estandarizada por edad vs. envejecimiento (tamaño = egresos)")
ax.set_ylim(0.1, 2.35)
lg = ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=4)
for h in lg.legend_handles: h.set_sizes([40])
fig.savefig(f"{FIG}/fig5_municipios_clusters.png"); plt.close(fig)

# ---- Fig 6: benchmark ----
b = json.load(open(f"{O}/benchmark.json")); r = pd.DataFrame(b["corridas"])
lab = {"pandas": "pandas (1 proceso)", "spark_1_csv": "Spark CSV, 1 núcleo",
       "spark_2_csv": "Spark CSV, 2 núcleos", "spark_2_parquet": "Spark Parquet, 2 núcleos"}
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3.2))
for i, (k, d) in enumerate(r.groupby("motor", sort=False)):
    ax1.plot(d.filas / 1e6, d.seg, color=CAT[i], lw=2, marker="o", ms=5, label=lab[k])
ax1.set_xlabel("Registros (millones)"); ax1.set_title("Tiempo de la consulta ICSAP (s)"); ax1.legend(fontsize=7.5)
t = b["tamanios"]; f = [1, 4, 16]
x = np.arange(3)
ax2.bar(x - 0.2, [t[f"x{i}_csv_MB"] for i in f], 0.38, color=CAT[1], label="CSV")
ax2.bar(x + 0.2, [t[f"x{i}_parquet_MB"] for i in f], 0.38, color=CAT[0], label="Parquet (snappy)")
for xi, i in zip(x, f):
    ax2.text(xi - 0.2, t[f"x{i}_csv_MB"] + 40, f"{t[f'x{i}_csv_MB']:,.0f}", ha="center", fontsize=7, color=INK2)
    ax2.text(xi + 0.2, t[f"x{i}_parquet_MB"] + 40, f"{t[f'x{i}_parquet_MB']:,.0f}", ha="center", fontsize=7, color=INK2)
ax2.set_xticks(x, [f"x{i}" for i in f]); ax2.set_title("Tamaño en disco (MB)"); ax2.legend(fontsize=8)
fig.savefig(f"{FIG}/fig6_benchmark.png"); plt.close(fig)
print("ok", os.listdir(FIG))
