#!/bin/bash
# Isi ulang folder utama dengan merek channel mayor (daftar di major_brands.yml) yang dicari di SEMUA entri sumber (11k+).
#   bash refill.sh          -> tes URL kandidat yang BELUM pernah dites, pilih yang lolos, build
#   bash refill.sh semua    -> tes ulang SEMUA kandidat merek mayor (lama)
# Jalankan dari WiFi rumah (MyRepublic), bukan hotspot. Menulis data/status_lokal.json, data/refill_pick.json, out/.
# Tidak perlu STB. Setelah selesai: upload build.py, major_brands.yml (opsional), data/status_lokal.json, data/refill_pick.json ke repo GitHub.
set -e
cd "$(dirname "$0")"
PY=python3; [ -x venv/bin/python ] && PY=venv/bin/python
$PY -c "import yaml" 2>/dev/null || { python3 -m venv venv && venv/bin/pip install -q pyyaml; PY=venv/bin/python; }
B="$PY build.py --index data/index.m3u --dhany data/dhanytv.m3u --draft draft_esensial.csv --dir data --out out --require-radio"
if [ "$1" = "semua" ]; then FLAG="--force"; else FLAG="--max-age-hours 99999"; fi
echo "1/5 build (keadaan folder utama sekarang)"; $B | sed -n 1,1p
echo "2/5 scan semua entri, cocokkan merek mayor"; $PY refill.py scan | sed -n 2,6p
echo "3/5 tes stream kandidat (${1:-baru saja}); beberapa menit"
$PY check_local.py out/refill_kandidat.json -o data/status_lokal.json --workers 8 --per-host 2 --timeout 10 --retries 2 $FLAG | tail -3
echo "4/5 build dengan status baru, lalu pilih"; $B | sed -n 1,1p; $PY refill.py apply | sed -n 1,2p
echo "5/5 build final"; $B | sed -n 1,3p
echo "SELESAI. Baca out/refill_laporan.txt (dinaikkan, tidak ada yang hidup, tidak ada di sumber). Playlist baru: out/playlist.m3u."
