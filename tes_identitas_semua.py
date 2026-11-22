import csv, glob, json, os, re, shutil, subprocess
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
base = os.path.expanduser('~/iptv_stb_privat')
mp = {'http-referrer': 'Referer', 'http-referer': 'Referer', 'http-user-agent': 'User-Agent', 'http-origin': 'Origin'}
ent = {}
for p in glob.glob(base + '/*.m3u') + glob.glob(base + '/serve/*.m3u'):
    cur = None
    for l in open(p, encoding='utf-8', errors='ignore').read().splitlines():
        l = l.strip()
        if l.startswith('#EXTINF'):
            cur = {'h': {}}
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
            ent.setdefault(l, cur)
            cur = None
rows = [r for r in csv.DictReader(open(base + '/tes_kandidat_semua.csv', encoding='utf-8')) if r['status'] == 'HIDUP_LOKAL']
uniq = {}
for r in rows:
    uniq.setdefault(r['url'], []).append(r)
items = list(uniq.items())
ff = shutil.which('ffmpeg')
d = base + '/fr2'
shutil.rmtree(d, ignore_errors=True)
os.makedirs(d)
def grab(i):
    u = items[i][0]
    hh = {'User-Agent': 'Mozilla/5.0'}
    hh.update(ent.get(u, {'h': {}})['h'])
    hs = ''.join('%s: %s\r\n' % (k, v) for k, v in hh.items())
    out = '%s/raw_%02d.jpg' % (d, i)
    try:
        subprocess.run([ff, '-y', '-loglevel', 'error', '-headers', hs, '-i', u, '-frames:v', '1', '-q:v', '3', out], timeout=40)
    except Exception:
        pass
    return os.path.exists(out)
with ThreadPoolExecutor(6) as ex:
    ok = list(ex.map(grab, range(len(items))))
n = 0
for i, (u, rs) in enumerate(items):
    if not ok[i]:
        print('frame gagal:', ' / '.join(x['nama'] for x in rs), '|', rs[0]['sumber'])
        continue
    n += 1
    os.rename('%s/raw_%02d.jpg' % (d, i), '%s/f_%02d.jpg' % (d, n))
    print(n, '|', ' / '.join(x['nama'] for x in rs), '|', rs[0]['sumber'], '|', rs[0]['group_sumber'], '| negara', rs[0]['negara'], '| host', urlparse(u).netloc)
subprocess.run([ff, '-y', '-loglevel', 'error', '-framerate', '1', '-i', d + '/f_%02d.jpg', '-vf', 'scale=320:180:force_original_aspect_ratio=decrease,pad=320:180:(ow-iw)/2:(oh-ih)/2,tile=5x5', '-frames:v', '1', d + '/sheet.jpg'])
print('sheet:', d + '/sheet.jpg')
