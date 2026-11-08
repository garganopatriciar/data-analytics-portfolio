#!/usr/bin/env bash
# Descarga idempotente de los egresos hospitalarios 2016-2022 (Portal de Datos Abiertos PBA).
# Si los CSV ya están en data/raw (o en egresos_raw.zip), no descarga nada y sólo verifica los checksums.
set -euo pipefail
RAW="$(cd "$(dirname "$0")/.." && pwd)/data/raw"; mkdir -p "$RAW"; cd "$RAW"
B=https://catalogo.datos.gba.gob.ar/dataset/baf07a7a-8cd2-47ad-bae0-52c6f3b45bb7/resource
declare -A F=(
  [egresos-2016.csv]=66e005f4-d88b-4abf-9797-5809def5131e/download/egresos-2016.csv
  [egresos-2017.csv]=3f9fd7e0-5d92-4b8c-a87b-951607637e89/download/egresos-2017.csv
  [egresos-2018.csv]=ddf7a32f-bc60-45b0-ad91-d3acd6813cd0/download/egresos-2018.csv
  [egresos-2019.csv]=6a839c98-9cbb-475a-840f-4b0e29c378e0/download/egresos-2019.csv
  [egresos-2020.csv]=06d4b138-11cb-4b72-a87b-bff09f6af07d/download/egresos-2020.csv
  [egresos-hospitalarios-2021.csv]=845079e1-53c8-4d0f-9fe8-854f690eac63/download/egresos-hospitalarios-2021.zip
  [egresos-hospitalarios-2022.csv]=1e4a0781-2049-400a-bfa1-ee5d80c94829/download/egresos-hospitalarios-2022.zip
)
# Los CSV vienen comprimidos en el repositorio (GitHub limita el tamaño por archivo)
if [ -f egresos_raw.zip ] && [ ! -s egresos-2016.csv ]; then unzip -o -q egresos_raw.zip; fi
for csv in "${!F[@]}"; do
  [ -s "$csv" ] && continue
  url="$B/${F[$csv]}"; echo "Descargando $csv"
  if [[ "$url" == *.zip ]]; then
    curl -fsSL --retry 3 -o tmp.zip "$url" && unzip -o -q tmp.zip && rm -f tmp.zip
  else
    curl -fsSL --retry 3 -o "$csv" "$url"
  fi
done
if [ -f checksums.sha256 ]; then
  sha256sum -c --quiet checksums.sha256 && echo "Checksums OK: datos idénticos a los del informe" \
    || echo "AVISO: los archivos difieren de la versión analizada en el informe (¿el portal los actualizó?)"
else
  sha256sum *.csv > checksums.sha256
fi
ls -la
