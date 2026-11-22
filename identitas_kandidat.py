import csv, os, re, json, shutil, subprocess, urllib.request
from urllib.parse import urlparse, urljoin
base = os.path.expanduser('~/iptv_stb_privat')
lines = open(base + '/gvision_20261116.m3u', encoding='utf-8', errors='ignore').read().splitlines()
mp = {'http-referrer': 'Referer', 'http-referer': 'Referer', 'http-user-agent': 'User-Agent', 'http-origin': 'Origin'}
ent = {}
cur = None
for l in lines:
    l = l.strip()
    if l.startswith('#EXTINF'):
        cur = {'extinf': l, 'nama': l.rsplit(',', 1)[-1].strip(), 'h': {}}
    elif cur is not None and l.startswith('#EXTVLCOPT:'):
        k, _, v = l[11:].partition('=')
        if k.lower() in mp:
            cur['h'][mp[k.lower()]] = v
    elif cur is not None and l.startswith('#EXTHTTP:'):
        try:
            cur['h'].update(json.loads(l[9:]))
        except Exception:
            pass
    elif cur is not None and l and not l.startswith('#'):
        ent[(cur['nama'], l)] = cur
        cur = None
def attr(s, k):
    m = re.search(k + '="([^"]*)"', s)
    return m.group(1) if m else ''
rows = list(csv.DictReader(open(base + '/tes_kandidat.csv', encoding='utf-8')))
ff = shutil.which('ffmpeg')
n = 0
for r in rows:
    if r['status'] != 'HIDUP_LOKAL':
        continue
    n += 1
    e = None
    for (nm, u), v in ent.items():
        if u == r['url']:
            e = v
            break
    if e is None:
        print(n, r['nama'], 'entri tidak ketemu')
        continue
    u = r['url']
    print('---', n, r['nama'], '| slot:', r['folder_tujuan'])
    print('   tvg-id:', attr(e['extinf'], 'tvg-id') or '-', '| tvg-name:', attr(e['extinf'], 'tvg-name') or '-', '| group:', r['group_sumber'], '| nama sumber:', e['nama'])
    print('   host stream:', urlparse(u).netloc, '| header dikirim:', ','.join(e['h'].keys()) or 'tidak ada')
    hh = {'User-Agent': 'Mozilla/5.0'}
    hh.update(e['h'])
    try:
        t = urllib.request.urlopen(urllib.request.Request(u, headers=hh), timeout=15).read(100000).decode('utf-8', 'ignore')
        res = re.findall(r'RESOLUTION=(\d+x\d+)', t)
        print('   resolusi di playlist:', ','.join(sorted(set(res))) or 'tidak tercantum')
    except Exception as x:
        print('   playlist gagal dibaca:', type(x).__name__)
    if ff:
        hs = ''.join('%s: %s\r\n' % (k, v) for k, v in hh.items())
        out = base + '/frame_%d_%s.jpg' % (n, re.sub('[^A-Za-z0-9]+', '_', r['nama']))
        try:
            subprocess.run([ff, '-y', '-loglevel', 'error', '-headers', hs, '-i', u, '-frames:v', '1', '-q:v', '3', out], timeout=40)
            print('   frame:', out if os.path.exists(out) else 'gagal')
        except Exception as x:
            print('   frame gagal:', type(x).__name__)
print('=== cek tiga TIDAK_DITEMUKAN: apa baris setelah EXTINF-nya')
for nama in ['Biznet Kids', 'My Kidz', 'HBO Hits']:
    for i, l in enumerate(lines):
        if l.startswith('#EXTINF') and l.rsplit(',', 1)[-1].strip() == nama:
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            nx = lines[j].strip() if j < len(lines) else ''
            print(nama, '->', 'EXTINF lain (tanpa URL)' if nx.startswith('#EXTINF') else ('opsi header' if nx.startswith('#') else 'URL'))
