import csv, json, re, shutil, yaml, collections

rules = yaml.safe_load(open('rules.yml', encoding='utf-8'))
M = yaml.safe_load(open('major_brands.yml', encoding='utf-8'))
lab = {f['label']: f for f in rules['folders']}
key2f = {f['key']: f for f in rules['folders']}
st = json.load(open('data/status_lokal.json', encoding='utf-8'))
SUF = set(M['suffix_words'])
cc2reg = {c: r for r, cs in M['region_cc'].items() for c in cs}
order = {r: i for i, r in enumerate(M['region_order'])}
AR = M['allowed_regions']
HINT = {r: [re.compile(p) for p in ps] for r, ps in M['region_hints'].items()}

def region(e):
    n = e['name'].lower()
    for r, ps in HINT.items():
        if any(p.search(n) for p in ps):
            return r
    return cc2reg.get(e['cc'], 'other')

def nrm(s):
    s = re.sub(r'\[[^\]]*\]|\([^)]*\)', ' ', s.lower()).replace('&', ' and ').replace('+', ' plus ')
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()

def cocok(name, aliases, x=None):
    s = nrm(name)
    if x and re.search(x, name, re.I):
        return False
    for a in aliases:
        a = nrm(a)
        if s == a or (s.startswith(a + ' ') and all(t in SUF for t in s[len(a):].split())):
            return True
    return False

ents, a, nm = [], {}, ''
for l in open('out/playlist.m3u', encoding='utf-8', errors='replace'):
    l = l.strip()
    if l.startswith('#EXTINF'):
        a = dict(re.findall(r'([\w-]+)="([^"]*)"', l))
        nm = l.split(',', 1)[1].strip() if ',' in l else ''
    elif l.startswith('http') and nm:
        s = st.get(l)
        m = re.search(r'\.([a-z]{2,3})(@|$)', a.get('tvg-id', ''))
        ents.append(dict(name=nm, tvg=a.get('tvg-id', ''), grup=a.get('group-title', ''), url=l,
                         ok=bool(s and s.get('ok')), h=(s or {}).get('height', 0) or 0, cc=m.group(1) if m else ''))
        nm = ''
main = [e for e in ents if e['grup'] in lab]
arch = [e for e in ents if e['grup'] not in lab]
idx_tvg = set()
for l in open('data/index.m3u', encoding='utf-8', errors='replace'):
    m = re.search(r'tvg-id="([^"]+)"', l)
    if l.startswith('#EXTINF') and m:
        idx_tvg.add(m.group(1).lower())

raw = open('draft_esensial.csv', encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in raw else '\n'
draft = list(csv.DictReader(open('draft_esensial.csv', encoding='utf-8-sig', newline='')))
fields = list(draft[0].keys())
shutil.copy('draft_esensial.csv', 'draft_esensial.csv.bak_v112s')
used = {d['tvg_id'].lower() for d in draft if d['tvg_id']}
tag = re.compile(r'\s\[(?:MATI|VPN|STB|BELUM)\]\s*$')

def bersih(n):
    n = re.sub(r'\s*\[Geo-blocked\]', '', n, flags=re.I)
    n = re.sub(r'\s*\((\d{3,4}[pi])\)', '', n)
    return re.sub(r'\s+', ' ', n).strip()

naik, tdk = [], []
for b in M['brands']:
    mm = [e for e in main if cocok(e['name'], b['a'], b.get('x')) and not tag.search(e['name']) and e['ok']]
    if mm:
        continue
    allowed = (set(b['r']) if b.get('r') else set(AR.get(b['f'], AR['default']))) - {'latam'}
    cand = []
    for e in arch:
        if e['ok'] and cocok(e['name'], b['a'], b.get('x')):
            rg = region(e)
            if rg in allowed and e['tvg'].lower() in idx_tvg and e['tvg'].lower() not in used:
                cand.append((order.get(rg, 9), -e['h'], rg, e))
    cand.sort(key=lambda x: x[:2])
    if not cand:
        tdk.append(b['n'])
        continue
    rg, e = cand[0][2], cand[0][3]
    f = key2f[b['f']]
    draft.append(dict(folder=f['csv'], nama=bersih(e['name']), tvg_id=e['tvg'], negara=e['cc'].upper(),
                      resolusi='', not_24_7='', geo_blocked='', pluto=''))
    used.add(e['tvg'].lower())
    naik.append((b['n'], f['label'], bersih(e['name']), e['tvg'], rg, e['h']))

with open('draft_esensial.csv', 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=fields, lineterminator=nl)
    w.writeheader()
    w.writerows(draft)
print('merek major dinaikkan ke folder utama:', len(naik), '| tanpa kandidat yang sesuai aturan wilayah:', len(tdk))
for x in naik:
    print('  %-24s -> %-26s %-34s %-8s %sp' % (x[0][:24], x[1][:26], x[2][:34], x[4], x[5]))
