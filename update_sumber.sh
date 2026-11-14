#!/bin/bash
# Tarik sumber terbaru (iptv-org, dhanytv, extra) + segarkan daftar id EPG, lalu build. Jalankan kapan saja; ini versi manual dari workflow harian GitHub.
#   bash update_sumber.sh
set -e
cd "$(dirname "$0")"
PY=python3; [ -x venv/bin/python ] && PY=venv/bin/python
$PY -c "import yaml" 2>/dev/null || { python3 -m venv venv && venv/bin/pip install -q pyyaml; PY=venv/bin/python; }
B="$PY build.py --index data/index.m3u --dhany data/dhanytv.m3u --draft draft_esensial.csv --dir data --out out --require-radio"
echo "1/4 tarik sumber"; $PY fetch_sources.py data
echo "2/4 build sementara"; $B >/dev/null
EPG=$($PY -c "import yaml;print(yaml.safe_load(open('rules.yml'))['epg']['url'])")
echo "3/4 segarkan id EPG dari $EPG"
if $PY epg_check.py --epg "$EPG" --playlist out/playlist.m3u --out data/epg_ids.new | sed -n 2,4p && [ -s data/epg_ids.new ]; then mv data/epg_ids.new data/epg_ids.txt; else echo "EPG gagal, epg_ids.txt lama dipakai"; fi
rm -f data/epg_ids.new
echo "4/4 build final"; $B | sed -n 1,3p
echo "SELESAI. Kalau ada channel baru: bash tes_lokal.sh (tes URL baru). Playlist: out/playlist.m3u"
