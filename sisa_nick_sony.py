import csv, shutil

KEEP = {'nickjr.ru@sd', 'nickelodeon.fr@sd', 'nickelodeon.de@sd', 'sonychannel.br@sd', 'sonymovies.us@sd'}
DROP = {'animalplanet.ru@sd', 'discoverychannel.it@sd', 'discoverychannel.cz@sd', 'hgtv.it@sd', 'hbo.cz@sd'}

raw = open('draft_esensial.csv', encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in raw else '\n'
cur = list(csv.DictReader(open('draft_esensial.csv', encoding='utf-8-sig', newline='')))
bak = list(csv.DictReader(open('draft_esensial.csv.bak_v112o', encoding='utf-8-sig', newline='')))
fields = list(bak[0].keys())
shutil.copy('draft_esensial.csv', 'draft_esensial.csv.bak_v112o2')
n = len(bak)
hasil = []
for i, r in enumerate(cur):
    tv = r['tvg_id'].lower()
    if i < n:
        hasil.append(bak[i] if tv in DROP else r)
    elif tv in KEEP:
        hasil.append(r)
print('baris sebelum:', len(cur), '| sesudah:', len(hasil), '| dikembalikan:', sum(1 for i, r in enumerate(cur) if i < n and r['tvg_id'].lower() in DROP), '| baris baru dibuang:', sum(1 for i, r in enumerate(cur) if i >= n and r['tvg_id'].lower() in DROP))
with open('draft_esensial.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields, lineterminator=nl)
    w.writeheader()
    w.writerows(hasil)
