#!/bin/bash
# Build, lalu sajikan playlist ke jaringan rumah untuk dites di HP dulu, lalu TiviMate. Ctrl+C untuk berhenti.
set -e
cd "$(dirname "$0")"
PY=python3; [ -x venv/bin/python ] && PY=venv/bin/python
$PY -c "import yaml" 2>/dev/null || { python3 -m venv venv && venv/bin/pip install -q pyyaml; PY=venv/bin/python; }
OUT=$($PY build.py --index data/index.m3u --dhany data/dhanytv.m3u --draft draft_esensial.csv --dir data --out out --require-radio); echo "$OUT" | sed -n 1,2p
IP=$( (ipconfig getifaddr en0 || ipconfig getifaddr en1 || echo IP-MAC-LO) 2>/dev/null | head -1 )
echo; echo "1) Buka di browser HP (Wi-Fi yang sama dengan STB):  http://$IP:8000/playlist.m3u"
echo "2) TiviMate: Add playlist > M3U playlist > URL yang sama. Mac jangan ditutup, terminal ini biarkan terbuka."; echo
CAF=""; command -v caffeinate >/dev/null 2>&1 && CAF="caffeinate -i"
cd out && exec $CAF python3 -m http.server 8000
