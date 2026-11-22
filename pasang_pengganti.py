import csv, re, shutil

MAP = {
 'Animal Planet (United Kingdom)': ('14 · Dokumenter & Sains', 'UK'),
 'Discovery Channel (India) HD (1080p)': ('09 · Amerika · TV & Kabel', 'IN'),
 'Discovery Channel (United Kingdom)': ('09 · Amerika · TV & Kabel', 'UK'),
 'HGTV (United States)': ('09 · Amerika · TV & Kabel', 'US'),
 'HBO (United States)': ('05 · Film & Series', 'US'),
 'Nick Jr. (India) (576p)': ('12 · Anak & Kartun', 'IN'),
 'Nickelodeon (India) (576p)': ('12 · Anak & Kartun', 'IN'),
 'Nickelodeon (United Kingdom)': ('12 · Anak & Kartun', 'UK'),
 'Sony Channel (Argentina) (1080p)': ('05 · Film & Series', 'AR'),
 'Sony Movies (Brazil) (720p)': ('05 · Film & Series', 'BR'),
}
CC = {'cz': 'CZ', 'pl': 'PL', 'fr': 'FR', 'br': 'BR', 'us': 'US', 'it': 'IT', 'uk': 'UK', 'in': 'IN', 'de': 'DE', 'es': 'ES'}

def bersih(n):
    n = re.sub(r'\s*\((\d{3,4}[pi])\)', '', n)
    return re.sub(r'\s+', ' ', n).strip()

cand = {}
for x in csv.DictReader(open('docs/selamatkan_ID.csv', encoding='utf-8-sig')):
    if x['hasil_ID'] == 'LOLOS' and x['sumber'] == 'iptv-org' and x['tvg_id'] and x['target'] in MAP:
        cand.setdefault(x['target'], []).append(x)

shutil.copy('draft_esensial.csv', 'draft_esensial.csv.bak_v112o')
raw = open('draft_esensial.csv', encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in raw else '\n'
draft = list(csv.DictReader(open('draft_esensial.csv', encoding='utf-8-sig', newline='')))
fields = list(draft[0].keys())
used = {d['tvg_id'].lower() for d in draft if d['tvg_id']}
log = []
for nm in MAP:
    lst = sorted(cand.get(nm, []), key=lambda x: -int(x['tinggi'] or 0))
    pick = next((c for c in lst if c['tvg_id'].lower() not in used), None)
    if not pick:
        log.append('%-36s TIDAK ADA kandidat bebas (id sudah dipakai slot lain)' % nm[:36])
        continue
    cid = pick['tvg_id']
    m = re.search(r'\.([a-z]{2})@', cid)
    negara = CC.get(m.group(1), '') if m else ''
    baru = bersih(pick['kandidat'])
    rows = [d for d in draft if d['nama'] == nm]
    if rows:
        rows[0]['nama'], rows[0]['tvg_id'], rows[0]['negara'] = baru, cid, negara or rows[0]['negara']
        aksi = 'ubah baris draft'
    else:
        draft.append(dict(folder=MAP[nm][0], nama=baru, tvg_id=cid, negara=negara or MAP[nm][1],
                          resolusi='', not_24_7='', geo_blocked='', pluto=''))
        aksi = 'baris draft baru'
    used.add(cid.lower())
    log.append('%-36s %s -> %s (%s)' % (nm[:36], aksi, baru[:34], cid))
with open('draft_esensial.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields, lineterminator=nl)
    w.writeheader()
    w.writerows(draft)
print('\n'.join(log))
