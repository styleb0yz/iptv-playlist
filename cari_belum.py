import csv, json, re, sys, time, threading, difflib, urllib.parse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import check_local as cl

sa = {x['nama'] for x in csv.DictReader(open('docs/status_akhir.csv', encoding='utf-8-sig'))}
rows = list(csv.DictReader(open('docs/revive_status_1511.csv', encoding='utf-8-sig')))
targets = [x for x in rows if x['status_baru'] == 'BELUM' and x['nama'] not in sa]
try:
    st = json.load(open('data/status_lokal.json', encoding='utf-8'))
except Exception:
    st = {}

def norm(s):
    s = re.sub(r'\(.*?\)|\[.*?\]', ' ', s.lower())
    s = re.sub(r'\b(hd|sd|fhd|uhd|\d{3,4}p|live|tv channel)\b', ' ', s)
    return re.sub(r'[^a-z0-9]+', '', s)

def parse(path, tag):
    out, attrs, opts, name = [], {}, [], ''
    for l in open(path, encoding='utf-8', errors='replace'):
        l = l.strip()
        if l.startswith('#EXTINF'):
            attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', l))
            name = l.split(',', 1)[1].strip() if ',' in l else ''
            opts = []
        elif l.startswith('#EXTVLCOPT') or l.startswith('#EXTHTTP') or l.startswith('#KODIPROP'):
            opts.append(l)
        elif l.startswith('http') and name:
            out.append(dict(url=l, name=name, attrs=attrs, opts=opts, src=tag))
            name, attrs, opts = '', {}, []
    return out

pool = []
for p, t in [('data/index.m3u', 'iptv-org'), ('data/dhanytv.m3u', 'dhanytv'),
             ('data/extra/gist_ahmadarif.m3u', 'gist'), ('data/extra/links_user.m3u', 'links_user')]:
    try:
        pool += parse(p, t)
    except OSError:
        print('lewati', p)
by = defaultdict(list)
for c in pool:
    by[norm(c['name'])].append(c)
keys = [k for k in by if len(k) >= 4]

REG = {'india': 'in', 'brazil': 'br', 'brasil': 'br', 'uk': 'uk', 'usa': 'us', 'united states': 'us',
       'germany': 'de', 'france': 'fr', 'italia': 'it', 'italy': 'it', 'spain': 'es', 'turkey': 'tr'}

def country(c):
    m = re.search(r'\.([a-z]{2,3})(@|$)', c['attrs'].get('tvg-id', ''))
    return m.group(1) if m else '?'

todo, info = [], []
for t in targets:
    nm = t['nama']
    k = norm(nm)
    if len(k) < 3:
        continue
    seen, cs = set(), []
    for c in by.get(k, []):
        cs.append((c, 'sama'))
    for kk in difflib.get_close_matches(k, keys, n=4, cutoff=0.9):
        if kk != k:
            for c in by[kk]:
                cs.append((c, 'mirip'))
    n = 0
    for c, how in cs:
        u = c['url']
        if u in seen or u in (t['url_lama'], t['url_sekarang']):
            continue
        seen.add(u)
        if n >= 6:
            break
        n += 1
        rg = [v for r, v in REG.items() if r in nm.lower()]
        flag = 'CEK_NEGARA' if rg and country(c) not in rg else ''
        c = dict(c, target=nm, kel=t['kelompok'], how=how, flag=flag)
        s = st.get(u)
        if s and s.get('ok') is False and s.get('checked', '') >= '2026-11-17':
            info.append((c, 'SUDAH_GAGAL_17NOV', s.get('reason', '')[:60], 0))
        elif s and s.get('ok'):
            info.append((c, 'SUDAH_LOLOS_DI_TES_LOKAL', '', s.get('height', 0)))
        else:
            todo.append(c)
print(f'target {len(targets)} | kandidat baru dites {len(todo)} | sudah punya hasil {len(info)}')

locks = defaultdict(lambda: threading.Semaphore(2))
def job(c):
    with locks[urllib.parse.urlparse(c['url']).netloc]:
        r = cl.check_one(c, 10)
        if not r['ok']:
            r = cl.check_one(c, 10)
    return c, r

res = []
with ThreadPoolExecutor(8) as ex:
    for c, r in ex.map(job, todo):
        res.append((c, 'LOLOS' if r['ok'] else 'GAGAL', r['reason'][:60], r.get('height', 0)))
allr = res + info
with open('docs/cari_belum_1711.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['target', 'kelompok', 'kandidat_nama', 'tvg_id', 'negara', 'cocok', 'flag', 'sumber', 'hasil', 'alasan', 'tinggi', 'url'])
    for c, h, a, ht in sorted(allr, key=lambda x: (x[0]['target'], x[1])):
        w.writerow([c['target'], c['kel'], c['name'], c['attrs'].get('tvg-id', ''), country(c), c['how'],
                    c['flag'], c['src'], h, a, ht, c['url']])
ok = [x for x in allr if x[1] in ('LOLOS', 'SUDAH_LOLOS_DI_TES_LOKAL')]
tg = sorted({x[0]['target'] for x in ok})
print(f'channel BELUM yang punya kandidat lolos: {len(tg)} dari {len(targets)}')
for c, h, a, ht in sorted(ok, key=lambda x: x[0]['target']):
    print(f"  {c['target'][:28]:28s} <- {c['name'][:32]:32s} {c['attrs'].get('tvg-id','')[:28]:28s} {c['src']:9s} {ht}p {c['how']} {c['flag']}")
print('detail lengkap: docs/cari_belum_1711.csv')
