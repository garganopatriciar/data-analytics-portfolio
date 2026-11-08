#!/usr/bin/env bash
# Uso:  bash run_all.sh          -> flujo completo (~10 min, el benchmark genera ~4 GB temporales)
#       bash run_all.sh rapido   -> todo menos el benchmark de escalabilidad (~3 min)
set -euo pipefail
cd "$(dirname "$0")/src"
bash 00_descarga.sh            # si los CSV ya están en data/raw no los vuelve a bajar
python3 01_ingesta_silver.py
python3 02_gold_analisis.py
bash 03_mapreduce/run_local.sh
python3 03_mapreduce/rdd_spark.py
python3 04_clustering_mllib.py
if [ "${1:-}" != "rapido" ]; then
  python3 05_benchmark_escalabilidad.py
  rm -rf ../data/bench
fi
python3 06_figuras.py
echo "Listo. Resultados en outputs/ y figuras en outputs/figuras/"
