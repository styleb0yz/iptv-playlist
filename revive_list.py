#!/usr/bin/env python3
# R1: daftar channel mati/rawan. Cuma BACA data, tidak mengubah playlist.
# Baca out/channels.json, out/kandidat_semua.json, data/status_lokal.json, data/refill_pick.json.
# Tulis docs/revive_list.csv.
import csv, json, re, collections, sys

def load(p):
    with open(p, encoding='utf-8') as f: return json.load(f)

ch  = load('out/channels.json')
ks  = {c['url']: c for c in load('out/kandidat_semua.json')}
st  = load('data/status_lokal.json')
pick = load('data/refill_pick.json')
latam_urls = {p['url']: p['brand'] for p in pick if p.get('region') == 'latam'}

def norm(s):
    s = s.lower()
    s = re.sub(r'\[[^\]]*\]|\([^)]*\)', ' ', s)
    s = s.replace('&', ' and ').replace('+', ' plus ')
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()

def status(url):
    s = st.get(url)
    if s is None: return 'belum_dites', '', 0, 0, False
    return ('lolos' if s.get('ok') else 'gagal'), (s.get('reason') or '')[:120], s.get('fails', 0), s.get('height', 0), bool(s.get('drm'))

by_canon = collections.defaultdict(list)
by_name  = collections.defaultdict(list)
for c in ch:
    by_canon[c['canon']].append(c)
    by_name[norm(c['name'])].append(c)

def alts(c):
    seen, out = {c['url']}, []
    for g in (by_canon.get(c['canon'], []), by_name.get(norm(c['name']), [])):
        for o in g:
            if o['url'] in seen: continue
            seen.add(o['url'])
            out.append(o)
    res = []
    for o in out:
        s = status(o['url'])[0]
        if s != 'gagal': res.append((o, s))
    res.sort(key=lambda t: (t[1] != 'lolos', t[0]['folder']))
    return res

def fnum(c):
    m = re.match(r'(\d+)', c['folder']); return int(m.group(1)) if m else 99

rows = []
for c in ch:
    n = fnum(c)
    s, reason, fails, h, drm = status(c['url'])
    grup = None
    if n <= 14 and s == 'gagal': grup = 'A_gagal_folder_utama'
    elif n <= 14 and s == 'belum_dites': grup = 'B_utama_belum_dites'
    elif n == 15 and s == 'belum_dites': grup = 'C_radio_belum_dites'
    elif n == 15 and s == 'gagal': grup = 'D_radio_gagal'
    elif c['folder'].endswith('Likely Dead'): grup = 'E_likely_dead'
    if n <= 14 and c['url'] in latam_urls:
        grup = (grup + '+' if grup else '') + 'F_varian_latam_spanyol'
    if not grup: continue
    a = alts(c)
    ok = [x for x in a if x[1] == 'lolos']; un = [x for x in a if x[1] == 'belum_dites']
    contoh = ' || '.join(f"{o['folder'][:2]}|{o['name']}|{sx}|{o['url']}" for o, sx in a[:3])
    k = ks.get(c['url'], {})
    rows.append([grup, c['name'], c['folder'], c.get('tvg', ''), k.get('country', ''), c['src'],
                 s, reason, fails, h, 'ya' if drm else '', len(ok), len(un), contoh, c['url']])

rows.sort(key=lambda r: (r[0], r[2], r[1]))
hdr = ['grup', 'nama', 'folder', 'tvg_id', 'negara', 'sumber', 'status', 'alasan_gagal', 'gagal_berturut',
       'resolusi', 'drm', 'alt_lolos', 'alt_belum_dites', 'alt_contoh_maks3', 'url']
with open('docs/revive_list.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f); w.writerow(hdr); w.writerows(rows)

print(f'ditulis docs/revive_list.csv: {len(rows)} baris')
cnt = collections.Counter(r[0] for r in rows)
for g in sorted(cnt):
    sub = [r for r in rows if r[0] == g]
    print(f'{g}: {cnt[g]} | punya alt lolos: {sum(1 for r in sub if r[11] > 0)} | punya alt belum dites: {sum(1 for r in sub if r[12] > 0 and r[11] == 0)} | tanpa alt: {sum(1 for r in sub if r[11] == 0 and r[12] == 0)}')
print('\nA. gagal folder utama:')
for r in rows:
    if r[0].startswith('A_'): print(f'  {r[2][:2]} {r[1]} | {r[7][:60]} | alt lolos={r[11]} belum={r[12]}')
dead = [r for r in rows if r[0].startswith('E_')]
print('\nE. likely dead per negara (top 12):', collections.Counter(r[4] or '?' for r in dead).most_common(12))
print('E. Indonesia di likely dead:', sum(1 for r in dead if (r[4] or '').lower() == 'id' or '.id' in r[3]))
tot = sum(1 for c in ch if fnum(c) <= 14)
bad = sum(1 for r in rows if r[0].startswith('A_'))
print(f'\nBaseline lokal folder utama tanpa radio: {tot-bad}/{tot} = {100*(tot-bad)/tot:.1f}%')
