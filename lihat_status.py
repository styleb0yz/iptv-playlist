import json, collections
from urllib.parse import urlparse
c = json.load(open('out/kandidat_cek.json'))
s = json.load(open('data/status_lokal.json'))
rows = []
for x in c:
    if x['country'] != 'id':
        continue
    r = s.get(x['url'])
    st = 'BELUM' if r is None else ('OK' if r['ok'] else 'GAGAL')
    rows.append((st, x['name'], urlparse(x['url']).netloc, (r or {}).get('reason', '')[:45]))
rows.sort(key=lambda t: (t[0] != 'OK', t[1].lower()))
print(collections.Counter(r[0] for r in rows))
for r in rows:
    print(f'{r[0]:5} {r[1][:34]:34} {r[2][:28]:28} {r[3]}')
