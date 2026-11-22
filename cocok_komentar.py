import csv, glob, json, os, re, unicodedata, collections
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse
base = os.path.expanduser('~/iptv_stb_privat')
QUAL = set('hd sd fhd uhd 4k 1080p 720p 576p 480p 432p 360p 240p tv channel the'.split())
mp = {'http-referrer': 'Referer', 'http-referer': 'Referer', 'http-user-agent': 'User-Agent', 'http-origin': 'Origin'}
def norm(s):
    s = s.lower()
    s = re.sub(r'\[[^\]]*\]|\([^)]*\)', ' ', s)
    s = s.replace('&', ' and ').replace('+', ' plus ')
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()
def loose(s):
    return ' '.join(t for t in norm(s).split() if t not in QUAL)
def parse(path):
    L = open(path, encoding='utf-8', errors='ignore').read().splitlines()
    out = []
    i = 0
    while i < len(L):
        l = L[i].strip()
        if not l.startswith('#EXTINF'):
            i += 1
            continue
        nama = l.rsplit(',', 1)[-1].strip()
        g = re.search(r'group-title="([^"]*)"', l)
        t = re.search(r'tvg-id="([^"]*)"', l)
        h = {}
        drm = False
        url = ''
        kom = False
        j = i + 1
        while j < len(L):
            x = L[j].strip()
            if not x:
                j += 1
                continue
            if x.startswith('#EXTVLCOPT:'):
                k, _, v = x[11:].partition('=')
                if k.lower() in mp:
                    h[mp[k.lower()]] = v
                j += 1
                continue
            if x.startswith('#EXTHTTP:'):
                try:
                    h.update(json.loads(x[9:]))
                except Exception:
                    pass
                j += 1
                continue
            if x.startswith('#KODIPROP'):
                drm = True
                j += 1
                continue
            m = re.match(r'^#+\s*(https?://\S+)', x)
            if m:
                url = m.group(1)
                kom = True
                break
            if x.startswith('#EXTINF'):
                break
            if x.startswith('#'):
                j += 1
                continue
            url = x
            break
        if url:
            neg = t.group(1).split('.')[-1].split('@')[0] if t and '.' in t.group(1) else '-'
            out.append({'nama': nama, 'group': g.group(1) if g else '', 'neg': neg, 'drm': drm, 'url': url, 'h': h, 'kom': kom})
            i = j + 1
        else:
            i = max(j, i + 1)
    return out
ex, lo = {}, {}
files = [p for p in glob.glob(base + '/*') + glob.glob(base + '/serve/*') if os.path.isfile(p) and os.path.getsize(p) < 8000000]
for p in files:
    if '#EXTINF' not in open(p, encoding='utf-8', errors='ignore').read():
        continue
    ent = parse(p)
    print('sumber', os.path.basename(p)[:30], ':', len(ent), 'entri,', sum(1 for e in ent if e['kom']), 'dikomentari')
    for e in ent:
        e['sumber'] = os.path.basename(p)
        ex.setdefault(norm(e['nama']), []).append(e)
        lo.setdefault(loose(e['nama']), []).append(e)
rows = [r for r in csv.DictReader(open('docs/revive_status_1511.csv', encoding='utf-8-sig')) if r['aman'] == 'belum' and r['kelompok'] != 'latam_audio_spanyol']
print('channel BELUM:', len(rows))
cands = []
for r in rows:
    c = ex.get(norm(r['nama']))
    tier = 'persis'
    if not c:
        k2 = loose(r['nama'])
        c = lo.get(k2) if len(k2) >= 3 else None
        tier = 'longgar'
    if not c:
        continue
    seen = set()
    for e in c:
        if e['url'] in seen:
            continue
        seen.add(e['url'])
        cands.append((r, tier, e))
print('kandidat untuk dites:', len(cands), 'dari', len(set(c[0]['nama'] for c in cands)), 'channel')
def get(u, h, rng=False):
    hh = {'User-Agent': 'Mozilla/5.0'}
    hh.update(h)
    if rng:
        hh['Range'] = 'bytes=0-2047'
    r = urllib.request.urlopen(urllib.request.Request(u, headers=hh), timeout=15)
    return r.status, r.read(2048 if rng else 300000)
def cek(u, h):
    try:
        s, b = get(u, h)
        t = b.decode('utf-8', 'ignore')
        if '#EXTM3U' not in t:
            return 'BUKAN_HLS'
        cu = u
        nu = u
        for _ in range(3):
            items = [x.strip() for x in t.splitlines() if x.strip() and not x.startswith('#')]
            if not items:
                return 'HLS_KOSONG'
            nu = urljoin(cu, items[0])
            if '.m3u8' in nu.split('?')[0].lower():
                cu = nu
                s, b = get(cu, h)
                t = b.decode('utf-8', 'ignore')
                if '#EXTM3U' not in t:
                    return 'BUKAN_HLS'
                continue
            break
        s2, b2 = get(nu, h, True)
        return 'HIDUP_LOKAL' if len(b2) > 0 else 'SEGMEN_KOSONG'
    except urllib.error.HTTPError as e:
        return 'HTTP_%d' % e.code
    except Exception as e:
        return 'GAGAL_' + type(e).__name__
def kerja(c):
    r, tier, e = c
    return 'DRM_BUTUH_STB' if e['drm'] else cek(e['url'], e['h'])
with ThreadPoolExecutor(8) as ex_:
    hasil = list(ex_.map(kerja, cands))
w = csv.writer(open(base + '/tes_komentar.csv', 'w', newline='', encoding='utf-8'))
w.writerow(['nama', 'kelompok', 'folder_tujuan', 'tier', 'sumber', 'nama_sumber', 'group_sumber', 'negara', 'komentar', 'status', 'url'])
for (r, tier, e), st in zip(cands, hasil):
    w.writerow([r['nama'], r['kelompok'], r['folder_tujuan'], tier, e['sumber'], e['nama'], e['group'], e['neg'], 'ya' if e['kom'] else '', st, e['url']])
print('=== ringkasan status:', dict(collections.Counter(hasil)))
print('=== HIDUP_LOKAL dan DRM')
for (r, tier, e), st in sorted(zip(cands, hasil), key=lambda z: z[0][0]['nama']):
    if st in ('HIDUP_LOKAL', 'DRM_BUTUH_STB'):
        print(r['nama'], '|', tier, '|', e['sumber'][:12], '|', e['group'][:22], '| negara', e['neg'], '| komentar' if e['kom'] else '|', st[:4], urlparse(e['url']).netloc[:28])
