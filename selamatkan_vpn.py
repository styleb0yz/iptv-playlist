import csv, json, os, re, subprocess, threading, difflib, urllib.parse, urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import check_local as cl

def negara():
    try:
        return urllib.request.urlopen('https://ipinfo.io/country', timeout=8).read().decode().strip()
    except Exception:
        return 'XX'

cc = negara()
if cc == 'ID':
    raise SystemExit('VPN belum aktif (IP negara: ID). Nyalakan VPN dulu.')

rows = {r['nama']: r for r in csv.DictReader(open('docs/revive_status_1511.csv', encoding='utf-8-sig'))}
targets = []
for x in csv.DictReader(open('docs/status_akhir.csv', encoding='utf-8-sig')):
    if x['kelompok'] == 'likely_dead' and 'DNS' not in x['alasan'] and x['nama'] in rows:
        targets.append(rows[x['nama']])

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
        pass
by = defaultdict(list)
for c in pool:
    by[norm(c['name'])].append(c)

def country(c):
    m = re.search(r'\.([a-z]{2,3})(@|$)', c['attrs'].get('tvg-id', ''))
    return m.group(1) if m else '?'

REG = {'india': 'in', 'brazil': 'br', 'brasil': 'br', 'uk': 'uk', 'united kingdom': 'uk', 'usa': 'us',
       'united states': 'us', 'germany': 'de', 'france': 'fr', 'italia': 'it', 'italy': 'it', 'spain': 'es', 'turkey': 'tr'}

todo = []
for t in targets:
    nm = t['nama']
    seen = set()
    cands = []
    for u in (t['url_lama'], t['url_sekarang']):
        if u and u not in seen:
            seen.add(u)
            cands.append(dict(url=u, name=nm, attrs={}, opts=[], src='slot'))
    for c in by.get(norm(nm), [])[:6]:
        if c['url'] not in seen:
            seen.add(c['url'])
            cands.append(c)
    rg = [v for r, v in REG.items() if r in nm.lower()]
    for c in cands:
        todo.append(dict(c, target=nm, flag='CEK_NEGARA' if (rg and c['src'] != 'slot' and country(c) not in rg) else ''))
print('IP negara:', cc, '| channel dites ulang:', len(targets), '| URL:', len(todo))

locks = defaultdict(lambda: threading.Semaphore(2))
def job(c):
    with locks[urllib.parse.urlparse(c['url']).netloc]:
        return c, cl.check_one(c, 12)

res = []
with ThreadPoolExecutor(10) as ex:
    for c, r in ex.map(job, todo):
        res.append((c, r))

with open('docs/selamatkan_%s.csv' % cc, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['target', 'sumber', 'kandidat', 'tvg_id', 'negara', 'flag', 'hasil', 'alasan', 'tinggi', 'url'])
    for c, r in res:
        w.writerow([c['target'], c['src'], c['name'], c['attrs'].get('tvg-id', ''), country(c), c['flag'],
                    'LOLOS' if r['ok'] else 'GAGAL', r['reason'][:60], r.get('height', 0), c['url']])

good = defaultdict(list)
for c, r in res:
    if r['ok']:
        good[c['target']].append((c, r))
out = os.path.expanduser('~/iptv_stb_privat/frame_selamat_%s' % cc)
os.makedirs(out, exist_ok=True)
print('channel yang punya URL lolos dari IP %s: %d dari %d' % (cc, len(good), len(targets)))

def ambil(a):
    i, (nm, lst) = a
    c, r = lst[0]
    f = '%s/%02d_%s.jpg' % (out, i, re.sub(r'[^A-Za-z0-9]+', '_', nm)[:40].strip('_'))
    try:
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-user_agent', 'Mozilla/5.0', '-allowed_extensions', 'ALL',
                        '-t', '10', '-i', c['url'], '-vf', 'fps=1,scale=480:-1', '-update', '1', f], timeout=50, capture_output=True)
    except Exception:
        pass
    fr = 'frame OK' if os.path.exists(f) and os.path.getsize(f) > 0 else 'tanpa frame'
    return '  %-36s <- %-26s %-14s %-7s %sp %s' % (nm[:36], c['name'][:26], c['attrs'].get('tvg-id', '')[:14], c['src'], r.get('height', 0), c['flag'] + ' ' + fr)

with ThreadPoolExecutor(4) as ex:
    for line in ex.map(ambil, list(enumerate(sorted(good.items()), 1))):
        print(line)
print('detail: docs/selamatkan_%s.csv | frame: %s' % (cc, out))
