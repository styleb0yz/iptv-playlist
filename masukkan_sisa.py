import csv, re, shutil, yaml, json, collections

rules = yaml.safe_load(open('rules.yml', encoding='utf-8'))
lab2key = {f['label']: f['key'] for f in rules['folders']}
rows = list(csv.DictReader(open('docs/revive_status_1511.csv', encoding='utf-8-sig')))
kw = {x['nama']: x['kategori_masalah'] for x in csv.DictReader(open('docs/revive_kerja.csv', encoding='utf-8-sig'))}
sa = {x['nama'] for x in csv.DictReader(open('docs/status_akhir.csv', encoding='utf-8-sig'))}
vpn = set()
for cc in ('US', 'GB'):
    try:
        for l in open('docs/vpn_hasil_%s.csv' % cc, encoding='utf-8'):
            if ',HIDUP,' in l:
                vpn.add(l.split(',')[0])
    except OSError:
        pass
STB_EXTRA = ('Antena 3', 'Mentari TV', 'My Kidz')
MATI_KAT = ('LINK_DIHAPUS_404', 'DOMAIN_MATI_DNS', 'LAINNYA')

def tag(r):
    n = r['nama']
    if n.replace(',', ' ') in vpn:
        return '[VPN]'
    if r['status_baru'] == 'TUNGGU_STB' or n.startswith(STB_EXTRA):
        return '[STB]'
    if n in sa or (kw.get(n) in MATI_KAT):
        return '[MATI]'
    return '[BELUM]'

def key(s):
    return re.sub(r'[^a-z0-9]+', '', re.sub(r'\[[^\]]*\]|\([^)]*\)', ' ', s.lower()))

pl = collections.defaultdict(list)
for l in open('out/playlist.m3u', encoding='utf-8', errors='replace'):
    if l.startswith('#EXTINF'):
        a = dict(re.findall(r'([\w-]+)="([^"]*)"', l))
        pl[key(l.split(',', 1)[1].strip())].append(a.get('group-title', ''))

idx = collections.defaultdict(list)
cur = None
for l in open('data/index.m3u', encoding='utf-8', errors='replace'):
    l = l.strip()
    if l.startswith('#EXTINF'):
        a = dict(re.findall(r'([\w-]+)="([^"]*)"', l))
        cur = (l.split(',', 1)[1].strip() if ',' in l else '', a.get('tvg-id', ''))
    elif l.startswith('http') and cur:
        if cur[1]:
            idx[cur[0]].append(cur[1].lower())
        cur = None

raw = open('draft_esensial.csv', encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in raw else '\n'
draft = list(csv.DictReader(open('draft_esensial.csv', encoding='utf-8-sig', newline='')))
fields = list(draft[0].keys())
by_tvg = {d['tvg_id'].lower(): d for d in draft if d['tvg_id']}
aman = {key(r['nama']) for r in rows if r['status_baru'].startswith('AMAN')}

todo = [r for r in rows if not r['status_baru'].startswith('AMAN')
        and not [g for g in pl.get(key(r['nama']), []) if not g.startswith('Archive')]]
shutil.copy('draft_esensial.csv', 'draft_esensial.csv.bak_v112r')
shutil.copy('rules.yml', 'rules.yml.bak_v112r')
shutil.copy('data/extra/links_user.m3u', 'data/extra/links_user.m3u.bak_v112r')
ren, ext, tanpa = 0, [], []
pins, gaps, entri = [], [], []
for r in todo:
    n = r['nama']
    t = tag(r)
    nt = n + ' ' + t
    dr = next((by_tvg[c] for c in idx.get(n, []) if c in by_tvg and key(by_tvg[c]['nama']) not in aman), None)
    if dr is not None:
        dr['nama'] = nt
        pins.append(nt)
        ren += 1
        continue
    u = r['url_lama'] or r['url_sekarang']
    fk = lab2key.get(r['folder_tujuan'])
    if not u or not fk:
        tanpa.append((n, 'tanpa URL' if not u else 'folder tidak dikenal'))
        continue
    slug = 'sisa.' + re.sub(r'[^a-z0-9]+', '', n.lower())
    entri += ['#EXTINF:-1 tvg-id="%s" group-title="Sisa",%s' % (slug, nt), u]
    gaps.append('  - {nama: %s, name_regex: %s, folder: %s}' % (json.dumps(nt, ensure_ascii=False), json.dumps('^' + re.escape(nt) + '$'), fk))
    pins.append(nt)
    ext.append(n)

with open('draft_esensial.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields, lineterminator=nl)
    w.writeheader()
    w.writerows(draft)
ry = open('rules.yml', encoding='utf-8').read()
lama = yaml.safe_load(ry).get('pin') or []
baru = lama + [p for p in pins if p not in lama]
ry, k = re.subn(r'(?m)^pin:.*$', lambda m: 'pin: ' + json.dumps(baru, ensure_ascii=False), ry, count=1)
assert k == 1
if gaps:
    ry, k2 = re.subn(r'(?m)^hold:', lambda m: '\n'.join(gaps) + '\nhold:', ry, count=1)
    assert k2 == 1
open('rules.yml', 'w', encoding='utf-8').write(ry)
if entri:
    open('data/extra/links_user.m3u', 'a', encoding='utf-8').write('\n# v112r: channel sisa yang entri sumbernya hilang dari index.m3u\n' + '\n'.join(entri) + '\n')
print('belum di folder utama:', len(todo), '| draft diganti nama:', ren, '| lewat entri extra dan gap:', len(ext), '| tidak bisa:', len(tanpa))
for x in tanpa:
    print('  %-36s %s' % (x[0][:36], x[1]))
