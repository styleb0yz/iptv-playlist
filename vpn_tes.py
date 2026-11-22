import csv, sys, urllib.request
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
def baca(u, n):
    r = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=10)
    return r.read(n)
def negara():
    try:
        return urllib.request.urlopen('https://ipinfo.io/country', timeout=8).read().decode().strip()
    except Exception:
        return 'XX'
def uji(u):
    try:
        for _ in range(3):
            b = baca(u, 60000)
            if b[:7] != b'#EXTM3U':
                return len(b) > 0
            ln = [l.strip() for l in b.decode('utf-8', 'ignore').splitlines() if l.strip() and not l.startswith('#')]
            if not ln:
                return False
            u = urljoin(u, ln[-1] if b'#EXTINF' in b else ln[0])
        return False
    except Exception:
        return False
cc = negara()
if cc == 'ID':
    print('VPN belum aktif (IP negara: ID). Nyalakan VPN dulu.')
    sys.exit()
kw = {r['nama']: r['kategori_masalah'] for r in csv.DictReader(open('docs/revive_kerja.csv', encoding='utf-8-sig'))}
rows = [r for r in csv.DictReader(open('docs/revive_status_1511.csv', encoding='utf-8-sig')) if r['status_baru'] == 'BELUM' and kw.get(r['nama']) == 'DIBLOK_403_GEOBLOK']
urls = [r['url_lama'] or r['url_sekarang'] for r in rows]
with ThreadPoolExecutor(12) as ex:
    ok = list(ex.map(uji, urls))
out = open('docs/vpn_hasil_%s.csv' % cc, 'w', encoding='utf-8')
n = 0
for r, u, o in zip(rows, urls, ok):
    out.write('%s,%s,%s\n' % (r['nama'].replace(',', ' '), 'HIDUP' if o else 'tidak', u.split('/')[2]))
    if o:
        n += 1
        print(r['nama'][:34], '|', u.split('/')[2][:30])
print('IP negara:', cc, '| segmen terambil:', n, 'dari', len(rows))
