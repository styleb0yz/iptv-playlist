import collections, csv, json, re, sys, yaml

def load(p):
    with open(p, encoding='utf-8') as f: return json.load(f)
def rcsv(p):
    with open(p, encoding='utf-8-sig', errors='replace') as f: return list(csv.DictReader(f.read().replace('\x00', '').splitlines()))

ch = load('out/channels.json'); st = load('data/status_lokal.json'); ks = {c['url']: c for c in load('out/kandidat_semua.json')}
rules = yaml.safe_load(open('rules.yml', encoding='utf-8'))
kerja = rcsv('docs/revive_kerja.csv'); draft = rcsv('draft_esensial.csv')
last = {}
for p in ('docs/tes_ketat.csv', 'docs/tes_ketat2.csv'):
    try:
        for r in rcsv(p): last[r['url']] = r
    except OSError: pass

def norm(s):
    s = s.lower(); s = re.sub(r'\[[^\]]*\]|\([^)]*\)', ' ', s); s = s.replace('&', ' and ').replace('+', ' plus ')
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()
QUAL = set('hd sd fhd uhd 4k 1080p 720p 576p 480p 432p 360p 240p tv channel the'.split())
def toks(x): return {t for t in norm(x).split() if t not in QUAL}
def fnum(c):
    m = re.match(r'(\d+)', c['folder']); return int(m.group(1)) if m else 99
def bersih(f): return re.sub(r'^\d+\s*·\s*', '', f)
def stat(u):
    s = st.get(u); return 'belum_dites' if s is None else ('lolos' if s.get('ok') else 'gagal')
VETTED = set(l.strip() for l in open('data/extra/links_user.m3u', encoding='utf-8').read().splitlines() if l.strip() and not l.startswith('#'))
VETTED |= set(l.strip() for l in open('data/vetted_urls.txt', encoding='utf-8').read().splitlines() if l.strip())
def ketat(u): return '' if u in VETTED else last.get(u, {}).get('verdict', '')

by_url = {c['url']: c for c in ch}
main = [c for c in ch if fnum(c) <= 15]
all_by_name = collections.defaultdict(list)
for c in ch: all_by_name[norm(c['name'])].append(c)

csv2key = {f['csv']: f for f in rules['folders']}
draft_slot = {}
for d in draft:
    n = norm(d['nama'])
    if n and d['folder'] in csv2key: draft_slot.setdefault(n, d['folder'])
for g in rules.get('gaps', []):
    draft_slot.setdefault(norm(g['nama']), next(f['csv'] for f in rules['folders'] if f['key'] == g['folder']))
try:
    for rp in load('data/refill_pick.json'):
        k = rp.get('folder')
        fc = next((f['csv'] for f in rules['folders'] if f['key'] == k), None)
        if fc:
            for nm in (rp.get('brand'), rp.get('label')):
                if nm: draft_slot.setdefault(norm(nm), fc)
except OSError: pass
RADIO_CSV = next(f['csv'] for f in rules['folders'] if f['key'] == 'radio')

KW = [
 ('islam', ['islam', 'quran', 'muslim', 'ajwa', 'ashiil', 'naajiya']),
 ('kids', ['kids', 'kidz', 'cartoon', 'nick', 'disney jr', 'disney junior', 'baby', 'jimjam', 'cbeebies', 'cbbc', 'boomerang', 'junior']),
 ('sports2', ['golf', 'nba', 'rugby']),
 ('sports', ['sport', 'espn', 'dazn', 'eurosport', 'f1', 'nfl', 'racer', 'overtime', 'fight', 'barca', 'bein', 'golazo', 'setanta', 'willow', 'one golf']),
 ('music', ['vevo', 'mtv', 'trace', 'dance', 'k pop', 'kpop', 'music']),
 ('docs', ['discovery', 'national geographic', 'animal planet', 'history', 'investigation', 'curiosity', 'nature', 'documentary', 'science', 'mythbusters']),
 ('intl_news', ['news', 'cnn', 'cnbc', 'rt', 'france 24', 'al jazeera', 'gb news', 'tv5monde']),
 ('movies', ['hbo', 'cinemax', 'starz', 'lifetime', 'movie', 'cinema', 'tcm', 'amc', 'fx', 'axn', 'celestial', 'sony', 'hallmark', 'baywatch', 'hell s kitchen', 'laff', 'dust', 'cinevault', 'mst3k', 'reelz', 'crime', 'cinecanal', 'comedy central', 'e', 'a and e', 'universal', 'tnt series']),
]
CTY = {'uk': 'uk', 'us': 'america', 'ca': 'america', 'fr': 'europe', 'de': 'europe', 'it': 'europe', 'es': 'europe', 'nl': 'europe',
       'se': 'europe', 'dk': 'europe', 'pl': 'europe', 'tr': 'europe', 'pt': 'europe', 'ru': 'europe', 'ee': 'europe', 'ie': 'uk'}
key2csv = {f['key']: f['csv'] for f in rules['folders']}

def usulan(nama, negara, kel):
    n = norm(nama); t = n.split()
    if kel == 'radio_non_hidup': return RADIO_CSV, 'kelompok radio'
    best = None
    for dn, fcsv in draft_slot.items():
        dt = dn.split()
        if dt and t[:len(dt)] == dt and (best is None or len(dt) > len(best[0].split())): best = (dn, fcsv)
    if best: return best[1], f'induk: {best[0]}'
    padded = f' {n} '
    for key, words in KW:
        for w in words:
            if len(w) <= 3:
                if w in t: return key2csv[key], f'kata kunci: {w}'
            elif f' {w} ' in padded or any(x.startswith(w) for x in t): return key2csv[key], f'kata kunci: {w}'
    k = CTY.get((negara or '').lower())
    if k: return key2csv[k], f'negara: {negara}'
    if (negara or '').lower() == 'id': return key2csv['national'], 'negara: id'
    return '', 'belum ada usulan'

def cty(u): return (ks.get(u, {}).get('country') or '').lower()
def cocok(row_name, row_canon, o, row_cty=''):
    if row_cty and cty(o['url']) and cty(o['url']) != row_cty.lower(): return False
    if norm(o['name']) == norm(row_name): return True
    if row_canon and row_canon == o['canon']:
        t1, t2 = toks(row_name), toks(o['name'])
        return bool(t1 and t2 and len(t1 & t2) / len(t1 | t2) >= 0.6)
    return False

out, usul = [], []
for i, r in enumerate(kerja, 1):
    u, nama, kel, neg = r['url'], r['nama'], r['kelompok'], r['negara']
    cur = by_url.get(u)
    canon = cur['canon'] if cur else (ks.get(u, {}).get('canon') or '')
    cands = [o for o in main if cocok(nama, canon, o, neg)]
    seen, cl = set(), []
    for o in cands:
        if o['url'] not in seen: seen.add(o['url']); cl.append(o)
    def rank(o):
        s = stat(o['url']); v = ketat(o['url'])
        bad = (v and v != 'HIDUP') or (o['url'] == u and r['verdict_terkini'] in ('MATI', 'gagal', 'BEKU') and s != 'lolos' and o['url'] not in VETTED)
        if bad: return (2, o['folder'])
        return (0 if (s == 'lolos' and not bad) else 1 if s == 'belum_dites' else 2, o['folder'])
    cl.sort(key=rank)
    best = cl[0] if cl and rank(cl[0])[0] <= 1 else None
    alt_arsip = [o for o in all_by_name.get(norm(nama), []) if fnum(o) > 15 and o['url'] != u and stat(o['url']) == 'lolos' and ketat(o['url']) in ('', 'HIDUP') and (not neg or not cty(o['url']) or cty(o['url']) == neg.lower())]
    lama_di_main = bool(cur and fnum(cur) <= 15)

    if kel == 'latam_audio_spanyol': status, cat = 'KEPUTUSAN_LATAM', 'butuh keputusan lo: buang atau pertahankan'
    elif r['aksi'] == 'TUNGGU_STB' and lama_di_main and stat(u) != 'gagal' and u not in VETTED: status, cat = 'TUNGGU_STB', 'ada di folder utama, tinggal tes putar di TiviMate/STB (DRM/MPD)'
    elif best:
        s = stat(best['url']); st_txt = 'lolos tes lokal Mac' if s == 'lolos' else 'URL belum dites lokal'
        status = 'AMAN_LOLOS_LOKAL' if s == 'lolos' else 'AMAN_BELUM_DITES'
        cat = ('URL sama, ' if best['url'] == u else 'URL pengganti, ') + st_txt
    elif lama_di_main: status, cat = 'BELUM_SLOT_ADA_URL_MATI', f"di folder utama, tapi tes lokal {stat(u)} dan tes ketat/R3a {r['verdict_terkini']} ({r['kategori_masalah']})"
    elif alt_arsip: status, cat = 'BELUM_ALT_LOLOS_DI_ARSIP', f'{len(alt_arsip)} alternatif lolos ada di arsip, belum dipromosi'
    else: status, cat = 'BELUM', 'tidak ada URL hidup di folder utama'
    aman = status.startswith('AMAN')
    if kel == 'latam_audio_spanyol': best = None

    n = norm(nama)
    sd = draft_slot.get(n) or (RADIO_CSV if kel == 'radio_non_hidup' else '')
    if not sd and kel != 'likely_dead':
        mf = (best or cur or {}).get('folder', '')
        sd = next((f['csv'] for f in rules['folders'] if bersih(f['label']) == bersih(mf) or f['csv'].split(' · ', 1)[-1] == bersih(mf)), '') if mf and fnum({'folder': mf}) <= 15 else ''
    if sd: tujuan, dasar = sd, 'slot draft/rules'
    else: tujuan, dasar = usulan(nama, neg, kel); dasar = 'USULAN ' + dasar
    if aman and best: sekarang = bersih(best['folder']); url_now = best['url']
    elif cur: sekarang = bersih(cur['folder']); url_now = cur['url']
    else: sekarang = 'tidak ada di playlist'; url_now = ''
    tuj = csv2key[tujuan]['label'] if tujuan in csv2key else ''
    out.append(dict(no=i, kelompok=kel, nama=nama, aksi_lama=r['aksi'], status_baru=status, aman='ya' if aman else 'belum',
                    keterangan=cat, tes_lokal_url_sekarang=stat(url_now) if url_now else '-', folder_sekarang=sekarang,
                    folder_tujuan=tuj, dasar_tujuan=dasar, url_lama=u, url_sekarang=url_now))
    if not sd and kel != 'latam_audio_spanyol': usul.append(dict(folder=tujuan, nama=nama, tvg_id='', negara=(neg or '').upper(), resolusi='', not_24_7='', geo_blocked='', pluto='', dasar=dasar, status_baru=status))

COL = list(out[0].keys())
with open('docs/revive_status_1511.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, COL); w.writeheader(); w.writerows(out)
UC = ['folder', 'nama', 'tvg_id', 'negara', 'resolusi', 'not_24_7', 'geo_blocked', 'pluto', 'dasar', 'status_baru']
with open('docs/usulan_slot_1511.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, UC); w.writeheader(); w.writerows(usul)

C = collections.Counter
print(f'baris: {len(out)} (253 bermasalah = likely_dead 213 + utama 24 + radio 16; latam 15 terpisah)')
print('per status_baru:', dict(C(o['status_baru'] for o in out)))
n253 = [o for o in out if o['kelompok'] != 'latam_audio_spanyol']
am = [o for o in n253 if o['aman'] == 'ya']
print(f"aman dari 253: {len(am)} (lolos lokal {sum(o['status_baru']=='AMAN_LOLOS_LOKAL' for o in am)}, belum dites {sum(o['status_baru']=='AMAN_BELUM_DITES' for o in am)}) = {100*len(am)/len(n253):.1f}%  | target 90% = 228")
print('per kelompok aman/total:', {k: f"{sum(1 for o in n253 if o['kelompok']==k and o['aman']=='ya')}/{sum(1 for o in n253 if o['kelompok']==k)}" for k in sorted({o['kelompok'] for o in n253})})
ld = [o for o in out if o['kelompok'] == 'likely_dead']
print(f"likely_dead tanpa slot draft/rules: {sum(o['dasar_tujuan'].startswith('USULAN') for o in ld)} dari {len(ld)}; usulan tanpa folder: {sum(1 for o in ld if o['dasar_tujuan'].startswith('USULAN') and not o['folder_tujuan'])}")
print('usulan per dasar:', dict(C(u['dasar'].split(':')[0] for u in usul)))
print('usulan per folder:', dict(C(u['folder'] for u in usul)))
