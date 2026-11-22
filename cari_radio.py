import csv, json, os, re, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
base = os.path.expanduser('~/iptv_stb_privat')
rows = [r for r in csv.DictReader(open('docs/revive_status_1511.csv', encoding='utf-8-sig')) if r['aman'] == 'belum' and r['kelompok'] == 'radio_non_hidup']
hosts = ['de1.api.radio-browser.info', 'nl1.api.radio-browser.info', 'at1.api.radio-browser.info']
def toks(n):
    n = re.sub(r'<[^>]*>', ' ', n)
    n = re.sub(r'&.*$', ' ', n)
    return [t for t in re.findall(r'[a-z0-9]+', n.lower()) if not t.isdigit() and t not in ('fm', 'am')]
def api(q):
    for h in hosts:
        try:
            u = 'https://%s/json/stations/search?%s' % (h, urllib.parse.urlencode({'name': q, 'countrycode': 'ID', 'hidebroken': 'true', 'limit': 30}))
            return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'iptv-revive/1.0'}), timeout=15).read().decode('utf-8', 'ignore'))
        except Exception:
            continue
    return []
def audio(u):
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0', 'Icy-MetaData': '0'}), timeout=10)
        ct = (r.headers.get('Content-Type') or '').lower()
        d = r.read(4096)
        if len(d) >= 1024 and 'html' not in ct and not d.lstrip().startswith(b'<'):
            return 'HIDUP'
        return 'BUKAN_AUDIO'
    except Exception as e:
        return 'GAGAL_' + type(e).__name__
tasks = []
for r in rows:
    t = toks(r['nama'])
    q = ' '.join(t[:3])
    seen = set()
    for s in api(q):
        u = s.get('url_resolved') or s.get('url')
        st = set(toks(s.get('name', '')))
        ov = len(set(t) & st) / max(1, len(set(t)))
        if u and u not in seen and ov >= 0.6:
            seen.add(u)
            tasks.append((r['nama'], q, s.get('name', ''), s.get('codec', ''), s.get('bitrate', ''), u))
with ThreadPoolExecutor(8) as ex:
    res = list(ex.map(lambda x: audio(x[5]), tasks))
w = csv.writer(open(base + '/tes_radio.csv', 'w', newline='', encoding='utf-8'))
w.writerow(['nama', 'query', 'nama_api', 'codec', 'bitrate', 'status', 'url'])
for t, s in zip(tasks, res):
    w.writerow([t[0], t[1], t[2], t[3], t[4], s, t[5]])
for r in rows:
    mine = [(t, s) for t, s in zip(tasks, res) if t[0] == r['nama']]
    hid = [(t, s) for t, s in mine if s == 'HIDUP']
    print(r['nama'][:40], '| kandidat', len(mine), '| hidup', len(hid))
    for t, s in hid[:2]:
        print('    ->', t[2][:40], '|', t[3], t[4], '|', urllib.parse.urlparse(t[5]).netloc[:30])
