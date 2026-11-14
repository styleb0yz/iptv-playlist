#!/usr/bin/env python3
"""Stasiun radio Indonesia dari Radio Browser API (countrycode=ID, urut votes) -> data/radio_cache.json.
Gagal tarik -> pakai cache terakhir. Exit 1 kalau hasil akhir (baru atau cache) nol stasiun."""
import json, os, re, sys, urllib.parse, urllib.request
from pathlib import Path

D = Path(sys.argv[1] if len(sys.argv) > 1 else 'data')
D.mkdir(parents=True, exist_ok=True)
cache = D / 'radio_cache.json'
LIMIT, MIN_GOOD = 100, 50
BASES = [os.environ['RADIO_API_BASE']] if os.environ.get('RADIO_API_BASE') else \
    [f'https://{h}.api.radio-browser.info' for h in ('de1', 'de2', 'fi1', 'at1', 'nl1')]
Q = urllib.parse.urlencode(dict(countrycode='ID', hidebroken='true', order='votes', reverse='true', limit=250))


def pull():
    last = ''
    for b in BASES:
        try:
            req = urllib.request.Request(f'{b}/json/stations/search?{Q}', headers={'User-Agent': 'iptv-playlist-builder/1.0'})
            return json.loads(urllib.request.urlopen(req, timeout=30).read().decode('utf-8'))
        except Exception as e:  # noqa: BLE001
            last = f'{b}: {type(e).__name__} {str(e)[:60]}'
            print('  gagal', last)
    raise RuntimeError(last)


def clean(x):
    return re.sub(r'\s+', ' ', x.replace(',', ' ')).strip()


try:
    rows, seen, out = pull(), set(), []
    for r in rows:
        url = (r.get('url_resolved') or r.get('url') or '').strip()
        name = clean(r.get('name') or '')
        if not (url.startswith('http') and name and r.get('lastcheckok', 1) == 1) or url in seen:
            continue
        seen.add(url)
        logo = r.get('favicon') or ''
        out.append(dict(name=name, url=url, logo=logo if logo.startswith('http') else '', votes=r.get('votes', 0),
                        codec=r.get('codec', ''), bitrate=r.get('bitrate', 0)))
        if len(out) >= LIMIT:
            break
    if out:
        cache.write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding='utf-8')
        print(f'radio: {len(out)} stasiun baru' + (f'  (WARNING: di bawah {MIN_GOOD})' if len(out) < MIN_GOOD else ''))
    else:
        raise RuntimeError('API membalas tapi 0 stasiun lolos filter')
except Exception as e:  # noqa: BLE001
    print(f'WARNING radio fetch gagal ({e}), pakai cache terakhir')
    try:
        n = len(json.loads(cache.read_text(encoding='utf-8')))
    except (OSError, ValueError):
        n = 0
    if n == 0:
        sys.exit('GAGAL: stasiun radio Indonesia nol (tidak ada cache).')
    print(f'radio: cache lama {n} stasiun')
