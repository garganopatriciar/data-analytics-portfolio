#!/usr/bin/env bash
# Simulación local del flujo Hadoop Streaming: map -> shuffle/sort -> reduce
# En un clúster:  hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
#   -files mapper.py,reducer.py -mapper mapper.py -reducer reducer.py \
#   -input /raw/egresos/*.csv -output /out/icsap_mr
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"; RAW="$DIR/../../data/raw"; OUT="$DIR/../../outputs"
mkdir -p "$OUT"
time (cat "$RAW"/*.csv | python3 "$DIR/mapper.py" | LC_ALL=C sort -k1,1 | python3 "$DIR/reducer.py" > "$OUT/mapreduce_resultado.tsv")
cat "$OUT/mapreduce_resultado.tsv"
