import csv, glob, json, os, shutil, subprocess
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
rows = [r for r in csv.DictReader(open(base + '/tes_kandidat_semua.csv', encoding='utf-8')) if r['status'] == 'HIDUP_LOKAL' and r['nama'].split()[0] in ('GTV', 'MNCTV', 'RCTI', 'GREAT!')]
uniq = {}
for r in rows:
    uniq.setdefault(r['url'], []).append(r)
ff = shutil.which('ffmpeg')
d = base + '/fr3'
shutil.rmtree(d, ignore_errors=True)
os.makedirs(d)
n = 0
for u, rs in uniq.items():
    hh = {'User-Agent': 'Mozilla/5.0'}
    hh.update(ent.get(u, {'h': {}})['h'])
    hs = ''.join('%s: %s\r\n' % (k, v) for k, v in hh.items())
    out = '%s/f_%02d.jpg' % (d, n + 1)
    try:
        subprocess.run([ff, '-y', '-loglevel', 'error', '-allowed_segment_extensions', 'ALL', '-extension_picky', '0', '-headers', hs, '-i', u, '-frames:v', '1', '-q:v', '3', out], timeout=90)
    except Exception as x:
        print('gagal', type(x).__name__)
    if os.path.exists(out):
        n += 1
        print(n, '|', ' / '.join(x['nama'] for x in rs), '|', rs[0]['sumber'], '| negara', rs[0]['negara'])
    else:
        print('frame gagal:', ' / '.join(x['nama'] for x in rs))
if n:
    subprocess.run([ff, '-y', '-loglevel', 'error', '-framerate', '1', '-i', d + '/f_%02d.jpg', '-vf', 'scale=320:180:force_original_aspect_ratio=decrease,pad=320:180:(ow-iw)/2:(oh-ih)/2,tile=3x2', '-frames:v', '1', d + '/sheet.jpg'])
    print('sheet:', d + '/sheet.jpg')
