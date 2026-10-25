#!/usr/bin/env bash
# Link the newest titan_core_chip report into this dashboard's data dir.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
SRC="${CHIP_REPORTS_DIR:-/home/wuminchin/TitanCore/titan_core_chip/reports}"
DEST="$ROOT/data"
mkdir -p "$DEST"
if [[ ! -d "$SRC" ]]; then
  echo "reports dir not found: $SRC" >&2
  exit 1
fi
latest_csv="$(find "$SRC" -maxdepth 1 -type f -name '20??-??-??.csv' | sort | tail -n 1)"
if [[ -z "${latest_csv}" ]]; then
  echo "no dated CSV in $SRC" >&2
  exit 1
fi
ln -sfn "$latest_csv" "$DEST/latest.csv"
if [[ -f "$SRC/latest.md" ]]; then
  ln -sfn "$SRC/latest.md" "$DEST/latest.md"
fi
# Keep a dated copy name visible to the date picker without duplicating bytes.
base="$(basename "$latest_csv")"
ln -sfn "$latest_csv" "$DEST/$base"
echo "linked $latest_csv -> $DEST/latest.csv"
