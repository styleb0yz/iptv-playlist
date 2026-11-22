import csv, os, json, urllib.request, urllib.error
from urllib.parse import urljoin
base = os.path.expanduser('~/iptv_stb_privat')
cand = list(csv.DictReader(open(base + '/kandidat_gvision.csv', encoding='utf-8')))
lines = open(base + '/gvision_20261116.m3u', encoding='utf-8', errors='ignore').read().splitlines()
ent = {}
cur = None
mp = {'http-referrer': 'Referer', 'http-referer': 'Referer', 'http-user-agent': 'User-Agent', 'http-origin': 'Origin'}
for l in lines:
    l = l.strip()
    if l.startswith('#EXTINF'):
        cur = {'nama': l.rsplit(',', 1)[-1].strip(), 'h': {}, 'drm': False}
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
        ent[(cur['nama'], l)] = cur
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
w = csv.writer(open(base + '/tes_kandidat.csv', 'w', newline='', encoding='utf-8'))
w.writerow(['nama', 'kelompok', 'folder_tujuan', 'group_sumber', 'status', 'url'])
for c in cand:
    e = ent.get((c['nama_sumber'], c['url']))
    if e is None:
        st = 'TIDAK_DITEMUKAN'
    elif e['drm']:
        st = 'DRM_BUTUH_STB'
    else:
        st = cek(c['url'], e['h'])
    print(c['nama'], '|', c['kelompok'], '|', c['group_sumber'], '|', st)
    w.writerow([c['nama'], c['kelompok'], c['folder_tujuan'], c['group_sumber'], st, c['url']])
