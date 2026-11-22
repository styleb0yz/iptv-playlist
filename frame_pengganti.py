import os, re, subprocess
from concurrent.futures import ThreadPoolExecutor

ids = ['AnimalPlanet.ru@SD', 'DiscoveryChannel.it@SD', 'DiscoveryChannel.cz@SD', 'HGTV.it@SD', 'HBO.cz@SD',
       'NickJr.ru@SD', 'Nickelodeon.fr@SD', 'Nickelodeon.de@SD', 'SonyChannel.br@SD', 'SonyMovies.us@SD']
ent = {}
cur = None
for l in open('out/playlist.m3u', encoding='utf-8', errors='replace'):
    l = l.strip()
    if l.startswith('#EXTINF'):
        a = dict(re.findall(r'([\w-]+)="([^"]*)"', l))
        cur = dict(id=a.get('tvg-id', ''), grup=a.get('group-title', ''), nama=l.split(',', 1)[1] if ',' in l else '', opts=[])
    elif cur and (l.startswith('#EXTVLCOPT') or l.startswith('#EXTHTTP')):
        cur['opts'].append(l)
    elif cur and l.startswith('http'):
        cur['url'] = l
        if cur['id'] in ids and not cur['grup'].startswith('Archive'):
            ent.setdefault(cur['id'], cur)
        cur = None
out = os.path.expanduser('~/iptv_stb_privat/frame_pengganti')
os.makedirs(out, exist_ok=True)

def ambil(a):
    i, k = a
    e = ent.get(k)
    if not e:
        return '%-26s TIDAK ADA di folder utama' % k
    ref = ua = ''
    for o in e['opts']:
        if 'referrer' in o.lower() or 'referer' in o.lower():
            ref = o.split('=', 1)[1]
        if 'user-agent' in o.lower():
            ua = o.split('=', 1)[1]
    fn = '%s/%02d_%s.jpg' % (out, i, re.sub(r'[^A-Za-z0-9]+', '_', e['nama'])[:40].strip('_'))
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-allowed_extensions', 'ALL', '-user_agent', ua or 'Mozilla/5.0']
    if ref:
        cmd += ['-headers', 'Referer: %s\r\n' % ref]
    cmd += ['-t', '15', '-i', e['url'], '-vf', 'fps=1,scale=480:-1', '-update', '1', fn]
    try:
        p = subprocess.run(cmd, timeout=70, capture_output=True, text=True)
        ok = os.path.exists(fn) and os.path.getsize(fn) > 0
        err = '' if ok else (p.stderr.strip().splitlines() or ['-'])[-1][:70]
    except Exception as ex:
        ok, err = False, type(ex).__name__
    return '%-26s %-14s %-38s %s %s' % (k, e['grup'][:14], e['nama'][:38], 'FRAME OK' if ok else 'GAGAL', err)

with ThreadPoolExecutor(4) as ex:
    for r in ex.map(ambil, list(enumerate(ids, 1))):
        print(r)
print('folder:', out)
