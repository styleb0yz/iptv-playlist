#!/bin/bash
B="$HOME/IPTV_BACKUP"
mkdir -p "$B/zip"
cd "$HOME/Downloads" || exit 1
bash "$HOME/Downloads/iptv/backup.sh" || { echo "BACKUP GAGAL, zip tidak dibuat, zip lama tidak dipindah"; exit 1; }
Z="iptv_kirim_$(date +%d%m_%H%M).zip"
TMP=".iptv_kirim_baru.tmp"
rm -f "$TMP"
zip -r "$TMP" iptv -x "iptv/venv/*" "iptv/out/*" "iptv/_arsip/*" "*/__pycache__/*" "*.DS_Store" > /dev/null || { echo "ZIP GAGAL, zip lama tidak dipindah"; rm -f "$TMP"; exit 1; }
unzip -tq "$TMP" > /dev/null || { echo "ZIP BARU RUSAK, zip lama tidak dipindah"; rm -f "$TMP"; exit 1; }
for f in iptv_kirim*.zip iptv_handoff*.zip; do
  [ -e "$f" ] || continue
  mv -n "$f" "$B/zip/$f"
  if [ ! -e "$f" ]; then echo "zip lama dipindah (bukan dihapus): $f"; else echo "zip lama TIDAK dipindah (nama sama sudah ada di backup): $f"; fi
done
mv "$TMP" "$Z"
ls -l "$Z"
