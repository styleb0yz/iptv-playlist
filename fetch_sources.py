#!/usr/bin/env python3
"""Tarik index.m3u (iptv-org) dan dhanytv.m3u ke data/. Kalau gagal atau hasilnya mencurigakan,
pakai salinan terakhir yang sudah ada di data/ (versi kemarin). Gagal total hanya kalau
belum pernah ada salinan sama sekali."""
import json, os, re, sys, time, urllib.request
from pathlib import Path

SRC = {
    'index.m3u': (os.environ.get('URL_IPTV', 'https://iptv-org.github.io/iptv/index.m3u'), 1000),
    'dhanytv.m3u': (os.environ.get('URL_DHANY', 'https://raw.githubusercontent.com/dhasap/dhanytv/main/dhanytv.m3u'), 100),
}
D = Path(sys.argv[1] if len(sys.argv) > 1 else 'data')
D.mkdir(parents=True, exist_ok=True)
# Sumber tambahan: extra_sources.txt, satu baris "nama URL" (baris kosong dan baris # diabaikan).
# Hasil disimpan di data/extra/nama.m3u. Kegagalan sumber tambahan tidak menggagalkan job.
EXTRA_NAMES = set()
xs = Path('extra_sources.txt')
if xs.exists():
    for line in xs.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2 or not re.fullmatch(r'[A-Za-z0-9_-]+', parts[0]):
            print(f'WARNING extra_sources.txt: baris dilewati: {line[:60]}')
            continue
        key = f'extra/{parts[0]}.m3u'
        SRC[key] = (parts[1].strip(), 1)
        EXTRA_NAMES.add(key)
status, fatal = {}, False
for name, (url, min_n) in SRC.items():
    f = D / name
    f.parent.mkdir(parents=True, exist_ok=True)
    old_n = f.read_text(encoding='utf-8', errors='replace').count('#EXTINF') if f.exists() else 0
    reason, data = '', None
    for i in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'iptv-playlist-builder'})
            data = urllib.request.urlopen(req, timeout=60).read().decode('utf-8-sig', 'replace')
            break
        except Exception as e:  # noqa: BLE001
            reason = f'{type(e).__name__}: {str(e)[:80]}'
            time.sleep(5 * (i + 1))
    if data is not None:
        n = data.count('#EXTINF')
        if not data.lstrip().startswith('#EXTM3U'):
            reason, data = 'bukan M3U', None
        elif n < min_n or (old_n and n < old_n * 0.8):
            reason, data = f'jumlah entri mencurigakan ({n}, sebelumnya {old_n})', None
    if data is not None:
        f.write_text(data, encoding='utf-8')
        status[name] = dict(status='ok', entries=n)
    elif f.exists():
        status[name] = dict(status='fallback (pakai versi kemarin)', entries=old_n, reason=reason)
        print(f'WARNING {name}: {reason}, pakai versi kemarin')
    else:
        status[name] = dict(status='GAGAL, belum ada salinan', entries=0, reason=reason)
        if name not in EXTRA_NAMES:
            fatal = True
(D / 'fetch_status.json').write_text(json.dumps(status, ensure_ascii=False, indent=1), encoding='utf-8')
print(json.dumps(status, ensure_ascii=False))
sys.exit(1 if fatal else 0)
