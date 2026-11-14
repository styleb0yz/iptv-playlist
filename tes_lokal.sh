#!/bin/bash
# Tes stream dari jaringan rumah lo (channel Indonesia cuma bisa dites dari sini), lalu build ulang.
#   bash tes_lokal.sh          -> tes URL yang BELUM pernah dites saja (cepat)
#   bash tes_lokal.sh semua    -> tes ulang SEMUA kandidat (lama; sebulan sekali cukup)
set -e
cd "$(dirname "$0")"
PY=python3; [ -x venv/bin/python ] && PY=venv/bin/python
$PY -c "import yaml" 2>/dev/null || { python3 -m venv venv && venv/bin/pip install -q pyyaml; PY=venv/bin/python; }
B="$PY build.py --index data/index.m3u --dhany data/dhanytv.m3u --draft draft_esensial.csv --dir data --out out --require-radio"
echo "1/3 build (menyusun daftar kandidat)"; OUT=$($B); echo "$OUT" | sed -n 1,2p
if [ "$1" = "semua" ]; then FLAG="--force"; else FLAG="--max-age-hours 99999"; fi
echo "2/3 tes stream (${1:-baru saja})"
$PY check_local.py out/kandidat_cek.json -o data/status_lokal.json --workers 8 --per-host 2 --timeout 10 --retries 2 $FLAG | tail -3
echo "3/3 build final"; OUT=$($B); echo "$OUT" | sed -n 1,3p
echo "SELESAI. Playlist baru: out/playlist.m3u. Kalau GitHub sudah aktif: upload data/status_lokal.json ke repo (timpa)."
