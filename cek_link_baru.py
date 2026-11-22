#!/usr/bin/env python3
# Tes link baru dari data/links_user.txt pakai tes_ketat (video maju, ffprobe). BACA saja, tidak mengubah playlist.
# Format baris:  Nama | URL | catatan/flag   (flag dari scrape_siap.txt: butuh-referer, bertoken, cek-drm)
# Output: docs/cek_link_baru.csv dan ringkasan di layar.
import csv, re, sys, urllib.parse
import check_local as cl
import tes_ketat as tk

tk.GAP = 12; tk.PER_HOST = 1

def bersih(n):
    n = re.sub(r'\[[^\]]*\]|\([^)]*\)', ' ', n)
    return re.sub(r'\s+', ' ', n).strip().lower()

kamus = {}
try:
    for r in csv.DictReader(open('docs/cari_link.csv', encoding='utf-8-sig')):
        kamus[bersih(r['nama_bersih'])] = r
except FileNotFoundError:
    print('peringatan: docs/cari_link.csv tidak ada, nama channel tidak dicocokkan')

items, seen = [], set()
for ln in open('data/links_user.txt', encoding='utf-8'):
    ln = ln.strip()
    if not ln or ln.startswith('#'): continue
    p = [x.strip() for x in ln.split('|')]
    if len(p) < 2 or not re.match(r'https?://', p[1]): print('dilewati (format salah):', ln[:80]); continue
    if p[1] in seen: continue
    seen.add(p[1]); items.append((p[0], p[1], ' | '.join(p[2:])))

print(f'{len(items)} link | ffprobe: {tk.FFPROBE or "TIDAK ADA"}', flush=True)
rows = []
for nama, url, cat in items:
    attrs = {}
    m = re.search(r'scrape:([^\s|]+)', cat)
    if 'butuh-referer' in cat and m: attrs = {'http-referrer': f'https://{m.group(1)}/'}
    v, why, r, ms = tk.run_one({'url': url, 'opts': [], 'attrs': attrs}, 12)
    k = kamus.get(bersih(nama))
    rows.append([nama, url, v, why, r.get('pv', ''), r.get('pa', '') + ('/' + r['lang'] if r.get('lang') else ''),
                 k['folder'] if k else 'TIDAK COCOK dengan cari_link.csv', k['negara'] if k else '', cat])
    print(f'  {v:10} {nama} | {r.get("pv","")} | {(why or "")[:60]}', flush=True)

with open('docs/cek_link_baru.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f); w.writerow(['nama', 'url', 'verdict', 'alasan', 'video', 'audio_bahasa', 'folder_target', 'negara', 'catatan']); w.writerows(rows)
hidup = [r for r in rows if r[2] == 'HIDUP']
print(f'\nditulis docs/cek_link_baru.csv: {len(rows)} link, {len(hidup)} HIDUP')
for r in rows:
    if r[6].startswith('TIDAK COCOK'): print('  nama tidak cocok dengan cari_link.csv:', r[0])
