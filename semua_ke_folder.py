import csv, re, shutil, yaml, collections, json

rules = yaml.safe_load(open('rules.yml', encoding='utf-8'))
lab2csv = {f['label']: f['csv'] for f in rules['folders']}
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

idx = collections.defaultdict(list)
cur = None
for l in open('data/index.m3u', encoding='utf-8', errors='replace'):
    l = l.strip()
    if l.startswith('#EXTINF'):
        a = dict(re.findall(r'([\w-]+)="([^"]*)"', l))
        cur = (l.split(',', 1)[1].strip() if ',' in l else '', a.get('tvg-id', ''))
    elif l.startswith('http') and cur:
        if cur[1]:
            idx[cur[0]].append(cur[1])
        cur = None

raw = open('draft_esensial.csv', encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in raw else '\n'
draft = list(csv.DictReader(open('draft_esensial.csv', encoding='utf-8-sig', newline='')))
fields = list(draft[0].keys())
shutil.copy('draft_esensial.csv', 'draft_esensial.csv.bak_v112q')
used = {d['tvg_id'].lower() for d in draft if d['tvg_id']}
byname = {d['nama']: d for d in draft}

def tag(r):
    n = r['nama']
    if n.replace(',', ' ') in vpn:
        return '[VPN]'
    if r['status_baru'] == 'TUNGGU_STB' or n.startswith(STB_EXTRA):
        return '[STB]'
    if n in sa or (kw.get(n) in MATI_KAT):
        return '[MATI]'
    return '[BELUM]'

ren = add = 0
gagal = []
pins = []
for r in rows:
    if r['status_baru'].startswith('AMAN'):
        continue
    n = r['nama']
    if re.search(r'\[(MATI|VPN|STB|BELUM)\]$', n):
        continue
    t = tag(r)
    if n in byname:
        byname[n]['nama'] = n + ' ' + t
        pins.append(n + ' ' + t)
        ren += 1
        continue
    csvf = lab2csv.get(r['folder_tujuan'])
    cid = next((c for c in idx.get(n, []) if c.lower() not in used), None)
    if not csvf or not cid:
        gagal.append((n, t))
        pins.append(n)
        continue
    m = re.search(r'\.([a-z]{2})@?', cid)
    draft.append(dict(folder=csvf, nama=n + ' ' + t, tvg_id=cid, negara=(m.group(1).upper() if m else ''),
                      resolusi='', not_24_7='', geo_blocked='', pluto=''))
    used.add(cid.lower())
    pins.append(n + ' ' + t)
    add += 1

with open('draft_esensial.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields, lineterminator=nl)
    w.writeheader()
    w.writerows(draft)
print('draft: ditambah', add, '| diganti nama', ren, '| tidak bisa lewat draft', len(gagal))

shutil.copy('rules.yml', 'rules.yml.bak_v112q')
ry = open('rules.yml', encoding='utf-8').read()
lama = yaml.safe_load(ry).get('pin') or []
baru = lama + [p for p in pins if p not in lama]
ry2, k = re.subn(r'(?m)^pin:.*$', lambda m: 'pin: ' + json.dumps(baru, ensure_ascii=False), ry, count=1)
assert k == 1, 'baris pin: tidak ketemu di rules.yml'
open('rules.yml', 'w', encoding='utf-8').write(ry2)
print('pin: dari', len(lama), 'jadi', len(baru))
