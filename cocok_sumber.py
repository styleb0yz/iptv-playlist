import csv, os, re, sys, unicodedata
base = os.path.expanduser('~/iptv_stb_privat')
QUAL = set('hd sd fhd uhd 4k 1080p 720p 576p 480p 432p 360p 240p tv channel the'.split())
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
    skipped = 0
    i = 0
    while i < len(L):
        l = L[i]
        if l.startswith('#EXTINF'):
            nama = l.rsplit(',', 1)[-1].strip()
            g = re.search(r'group-title="([^"]*)"', l)
            t = re.search(r'tvg-id="([^"]*)"', l)
            drm = False
            j = i + 1
            while j < len(L) and (not L[j].strip() or L[j].startswith(('#EXTVLCOPT', '#EXTHTTP', '#KODIPROP'))):
                if L[j].startswith('#KODIPROP'):
                    drm = True
                j += 1
            u = L[j].strip() if j < len(L) else ''
            if u and not u.startswith('#'):
                out.append({'nama': nama, 'group': g.group(1) if g else '', 'tid': t.group(1) if t else '', 'drm': drm, 'url': u})
            else:
                skipped += 1
            i = j
        else:
            i += 1
    return out, skipped
srcs = {}
for p in sys.argv[1:]:
    e, sk = parse(p)
    srcs[os.path.basename(p)] = e
    print('sumber', os.path.basename(p), ':', len(e), 'entri, dilewati (URL dikomentari atau kosong):', sk)
rows = [r for r in csv.DictReader(open('docs/revive_status_1511.csv', encoding='utf-8-sig')) if r['aman'] == 'belum']
print('channel belum aman:', len(rows))
ex = {}
lo = {}
for sn, ent in srcs.items():
    for e in ent:
        ex.setdefault(norm(e['nama']), []).append((sn, e))
        lo.setdefault(loose(e['nama']), []).append((sn, e))
w = csv.writer(open(base + '/kandidat_semua_sumber.csv', 'w', newline='', encoding='utf-8'))
w.writerow(['nama', 'kelompok', 'folder_tujuan', 'tier', 'sumber', 'nama_sumber', 'group_sumber', 'tvg_negara', 'drm', 'url'])
hit = {}
for r in rows:
    k = norm(r['nama'])
    tier = 'persis'
    c = ex.get(k)
    if not c:
        k2 = loose(r['nama'])
        c = lo.get(k2) if k2 else None
        tier = 'longgar'
    if not c:
        continue
    seen = set()
    for sn, e in c:
        if e['url'] in seen:
            continue
        seen.add(e['url'])
        neg = e['tid'].split('.')[-1].split('@')[0] if '.' in e['tid'] else '-'
        w.writerow([r['nama'], r['kelompok'], r['folder_tujuan'], tier, sn, e['nama'], e['group'], neg, 'ya' if e['drm'] else '', e['url']])
        hit.setdefault((r['nama'], r['kelompok']), []).append((tier, sn, e['group'], neg, 'DRM' if e['drm'] else ''))
for (nama, kel), v in hit.items():
    print(nama, '|', kel, '|', len(v), 'URL |', v[0][0], '|', v[0][1], '|', v[0][2], '| negara', v[0][3], v[0][4])
print('channel punya kandidat:', len(hit), 'dari', len(rows))
