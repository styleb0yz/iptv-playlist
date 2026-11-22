import csv, os, re, subprocess, urllib.request
from concurrent.futures import ThreadPoolExecutor

def negara():
    try:
        return urllib.request.urlopen('https://ipinfo.io/country', timeout=8).read().decode().strip()
    except Exception:
        return 'XX'

cc = negara()
if cc == 'ID':
    raise SystemExit('VPN belum aktif (IP negara: ID). Nyalakan VPN dulu.')
hasil = 'docs/vpn_hasil_%s.csv' % cc
if not os.path.exists(hasil):
    raise SystemExit('belum ada %s, jalankan python3 vpn_tes.py dulu' % hasil)
hidup = [l.split(',')[0] for l in open(hasil, encoding='utf-8') if ',HIDUP,' in l]
url = {}
for r in csv.DictReader(open('docs/revive_status_1511.csv', encoding='utf-8-sig')):
    url[r['nama'].replace(',', ' ')] = r['url_lama'] or r['url_sekarang']
out = os.path.expanduser('~/iptv_stb_privat/frame_%s' % cc)
os.makedirs(out, exist_ok=True)

def ambil(a):
    i, nm = a
    u = url.get(nm)
    f = '%s/%02d_%s.jpg' % (out, i, re.sub(r'[^A-Za-z0-9]+', '_', nm)[:40].strip('_'))
    if not u:
        return nm, 'URL tidak ditemukan'
    try:
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-user_agent', 'Mozilla/5.0', '-t', '10', '-i', u,
                        '-vf', 'fps=1,scale=480:-1', '-update', '1', f], timeout=50, capture_output=True)
    except Exception as e:
        return nm, 'gagal: %s' % type(e).__name__
    return nm, 'OK' if os.path.exists(f) and os.path.getsize(f) > 0 else 'tidak ada frame'

with ThreadPoolExecutor(4) as ex:
    for nm, s in ex.map(ambil, list(enumerate(hidup, 1))):
        print('%-48s %s' % (nm[:48], s))
print('folder:', out)
