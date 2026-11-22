#!/bin/bash
set -e
SRC="$HOME/Downloads/iptv"
DST="$HOME/IPTV_BACKUP/snapshot/iptv_$(date +%d%m_%H%M)"
mkdir -p "$DST"
rsync -a --exclude '/venv' --exclude '/out' --exclude '/_arsip' --exclude '__pycache__' --exclude '.DS_Store' "$SRC/" "$DST/"
echo "snapshot: $DST"
du -sh "$DST"
