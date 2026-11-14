import json, re, urllib.parse as up
import check_local as c
cand = [x for x in json.load(open('out/kandidat_cek.json')) if x['name'] == 'BET Pluto TV'][0]
h = c.headers_for(cand)
print('URL', cand['url'])
st, d, base = c.fetch(cand['url'], h, 10, 600000)
print('1) http', st, '| akhir:', base[:100]); print(d[:300])
lines = [l.strip() for l in d.decode('utf-8', 'replace').splitlines() if l.strip()]
v = [l for l in lines if not l.startswith('#')]
if any(l.startswith('#EXT-X-STREAM-INF') for l in lines):
    st, d, base = c.fetch(up.urljoin(base, v[-1]), h, 10, 600000)
    print('2) variant http', st); print(d[:300])
    lines = [l.strip() for l in d.decode('utf-8', 'replace').splitlines() if l.strip()]
    v = [l for l in lines if not l.startswith('#')]
seg = up.urljoin(base, v[-1])
st, d, _ = c.fetch(seg, h, 10, 65536)
print('3) segmen', seg[:100], '| http', st, '| ukuran', len(d)); print('byte awal:', d[:40])
