#!/bin/bash
cd ~/Downloads || exit 1
rm -f iptv_kirim*.zip
zip -r "iptv_kirim_$(date +%d%m_%H%M).zip" iptv -x "iptv/venv/*" "iptv/out/*" "iptv/_arsip/*" "*/__pycache__/*" "*.DS_Store" > /dev/null
ls -l iptv_kirim*.zip
