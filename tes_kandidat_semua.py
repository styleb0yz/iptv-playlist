import csv, glob, json, os, urllib.request, urllib.error
from urllib.parse import urljoin
base = os.path.expanduser('~/iptv_stb_privat')
mp = {'http-referrer': 'Referer', 'http-referer': 'Referer', 'http-user-agent': 'User-Agent', 'http-origin': 'Origin'}
ent = {}
for p in glob.glob(base + '/*.m3u') + glob.glob(base + '/serve/*.m3u'):
    cur = None
    for l in open(p, encoding='utf-8', errors='ignore').read().splitlines():
        l = l.strip()
        if l.startswith('#EXTINF'):
            cur = {'h': {}, 'drm': False}
        elif cur is not None and l.startswith('#EXTVLCOPT:'):
            k, _, v = l[11:].partition('=')
            if k.lower() in mp:
                cur['h'][mp[k.lower()]] = v
        elif cur is not None and l.startswith('#EXTHTTP:'):
            try:
                cur['h'].update(json.loads(l[9:]))
            except Exception:
                pass
        elif cur is not None and l.startswith('#KODIPROP'):
            cur['drm'] = True
        elif cur is not None and l and not l.startswith('#'):
            ent.setdefault(l, cur)
            cur = None
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
rows = list(csv.DictReader(open(base + '/kandidat_semua_sumber.csv', encoding='utf-8')))
w = csv.writer(open(base + '/tes_kandidat_semua.csv', 'w', newline='', encoding='utf-8'))
w.writerow(['nama', 'kelompok', 'folder_tujuan', 'tier', 'sumber', 'nama_sumber', 'group_sumber', 'negara', 'status', 'url'])
for r in rows:
    e = ent.get(r['url'])
    if e is None:
        st = 'TIDAK_DITEMUKAN'
    elif r['drm'] or e['drm']:
        st = 'DRM_BUTUH_STB'
    else:
        st = cek(r['url'], e['h'])
    print(r['nama'], '|', r['tier'], '|', r['sumber'], '|', r['nama_sumber'], '|', r['group_sumber'], '| negara', r['tvg_negara'], '|', st)
    w.writerow([r['nama'], r['kelompok'], r['folder_tujuan'], r['tier'], r['sumber'], r['nama_sumber'], r['group_sumber'], r['tvg_negara'], st, r['url']])
