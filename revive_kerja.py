#!/usr/bin/env python3
# R3a: daftar kerja revive. BACA saja, tidak mengubah playlist. Tulis docs/revive_kerja.csv.
# Baca: out/channels.json, out/kandidat_semua.json, data/status_lokal.json, docs/tes_ketat.csv (R2), docs/tes_ketat2.csv (R2b, menimpa R2).
import collections, csv, json, re, sys

def load(p):
    with open(p, encoding='utf-8') as f: return json.load(f)
def rcsv(p):
    with open(p, encoding='utf-8-sig', errors='replace') as f: return list(csv.DictReader(f.read().replace('\x00', '').splitlines()))

ch = load('out/channels.json'); ks = {c['url']: c for c in load('out/kandidat_semua.json')}; st = load('data/status_lokal.json')
by = {c['url']: c for c in ch}
last = {}
for r in rcsv('docs/tes_ketat.csv'): last[r['url']] = r
try:
    for r in rcsv('docs/tes_ketat2.csv'): last[r['url']] = r
except OSError: print('catatan: docs/tes_ketat2.csv tidak ada, pakai R2 saja')

def norm(s):
    s = s.lower(); s = re.sub(r'\[[^\]]*\]|\([^)]*\)', ' ', s); s = s.replace('&', ' and ').replace('+', ' plus ')
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()
def stat(u):
    s = st.get(u); return 'belum_dites' if s is None else ('lolos' if s.get('ok') else 'gagal')
def fnum(c):
    m = re.match(r'(\d+)', c['folder']); return int(m.group(1)) if m else 99

by_canon = collections.defaultdict(list); by_name = collections.defaultdict(list)
for c in ch: by_canon[c['canon']].append(c); by_name[norm(c['name'])].append(c)
QUAL = set('hd sd fhd uhd 4k 1080p 720p 576p 480p 432p 360p 240p tv channel the'.split())
def toks(x): return {t for t in norm(x).split() if t not in QUAL}
def cty(c): return (ks.get(c['url'], {}).get('country') or '').lower()
def cocok(c, o):
    if o['url'] == c['url']: return False
    if cty(o) and cty(c) and cty(o) != cty(c): return False
    if norm(o['name']) == norm(c['name']): return True
    if c['canon'] and c['canon'] == o['canon']:
        t1, t2 = toks(c['name']), toks(o['name'])
        return bool(t1 and t2 and len(t1 & t2) / len(t1 | t2) >= 0.6)
    return False
def alts(c):
    seen, out = {c['url']}, []
    for g in (by_name.get(norm(c['name']), []), by_canon.get(c['canon'], []) if c['canon'] else []):
        for o in g:
            if o['url'] in seen or not cocok(c, o): continue
            seen.add(o['url']); out.append(o)
    res = [(o, stat(o['url'])) for o in out if stat(o['url']) != 'gagal']
    res.sort(key=lambda t: (t[1] != 'lolos', t[0]['folder'])); return res

def kategori(verdict, alasan):
    a = alasan.lower()
    if verdict == 'DRM': return 'DRM_BELUM_TERBUKTI'
    if verdict == 'MPD_TIDAK_DIUJI': return 'DASH_BELUM_DIUJI'
    if verdict == 'BEKU': return 'PLAYLIST_BEKU'
    if '429' in a: return 'RATE_LIMIT_429'
    if '404' in a or 'not found' in a or 'not available' in a: return 'LINK_DIHAPUS_404'
    if '403' in a or '401' in a or 'forbidden' in a or 'geoblock' in a: return 'DIBLOK_403_GEOBLOK'
    if 'nodename' in a or 'name or service' in a or 'getaddrinfo' in a: return 'DOMAIN_MATI_DNS'
    if 'timed out' in a or 'timeout' in a: return 'HOST_TIDAK_MERESPONS'
    if 'refused' in a or 'reset' in a or 'remotedisconnected' in a or 'incompleteread' in a or 'badstatusline' in a: return 'KONEKSI_DITOLAK_PUTUS'
    if '400' in a: return 'REQUEST_DITOLAK_400'
    if 'text/html' in a: return 'BUKAN_STREAM_HTML'
    if 'byte' in a or 'segmen' in a: return 'STREAM_KOSONG_RUSAK'
    if 'ffprobe' in a: return 'SEGMEN_TIDAK_TERBACA'
    return 'LAINNYA'

def host(u): return re.sub(r'^https?://', '', u).split('/')[0][:40]
rows = []
def add(prio, aksi, kel, c, verdict, alasan, a, minta):
    ok = [x for x in a if x[1] == 'lolos']; un = [x for x in a if x[1] == 'belum_dites']
    ct = ' || '.join(f"{o['folder'][:2]}|{o['name']}|{sx}|{o['url']}" for o, sx in a[:3])
    rows.append([prio, aksi, kel, c['name'], c['folder'], (ks.get(c['url'], {}).get('country') or '').lower(), verdict, kategori(verdict, alasan), alasan[:70], host(c['url']), len(ok), len(un), ct, minta, c['url']])

def aksi_dari_alt(a, verdict, alasan):
    ok = [x for x in a if x[1] == 'lolos']; un = [x for x in a if x[1] == 'belum_dites']
    if '429' in alasan: return 'TES_ULANG_LAMBAT', 'tidak ada, tes ulang pelan dari jaringan lain'
    if ok: return 'PROMOSI_ALT', 'konfirmasi: pakai alternatif yang sudah lolos (go promosi)'
    if un: return 'TES_ALT', 'tidak ada, gue tes alternatif dulu (R3b)'
    return 'CARI_LINK', 'LINK pengganti (dari STB, m3u lo, atau sumber publik)'

# 1+2: folder utama dan radio, verdict terkini bukan HIDUP
for u, r in last.items():
    if u not in by or r['verdict'] == 'HIDUP': continue
    c = by[u]; n = fnum(c); a = alts(c); kel = 'radio_non_hidup' if n == 15 else 'utama_non_hidup'
    v = r['verdict']
    cn = (ks.get(u, {}).get('country') or '').lower()
    prio = 'P1' if (cn == 'id' and n <= 14) else ('P2' if n <= 14 else 'P3')
    if v in ('DRM', 'MPD_TIDAK_DIUJI'): add(prio, 'TUNGGU_STB', kel, c, v, r['alasan'], a, 'tes putar di STB/TiviMate (lisensi tidak bisa dibuktikan dari Mac)')
    else:
        ak, mn = aksi_dari_alt(a, v, r['alasan']); add(prio, ak, kel, c, v, r['alasan'], a, mn)

# 3: Likely Dead
for c in ch:
    if not c['folder'].endswith('Likely Dead'): continue
    a = alts(c); cn = (ks.get(c['url'], {}).get('country') or '').lower()
    ok_main = [x for x in a if x[1] == 'lolos' and fnum(x[0]) <= 14 and last.get(x[0]['url'], {}).get('verdict', 'HIDUP') == 'HIDUP']
    s = st.get(c['url'], {}); alasan = s.get('reason', '')
    if ok_main: add('P5', 'SUDAH_TERCOVER', 'likely_dead', c, 'gagal', alasan, a, 'tidak ada, channel ini sudah punya pengganti hidup di folder utama')
    else:
        ak, mn = aksi_dari_alt(a, 'gagal', alasan)
        add('P3' if cn == 'id' else 'P4', ak, 'likely_dead', c, 'gagal', alasan, a, mn)

# 4: latam (HIDUP tapi audio spa/por), daftar terpisah
pick = load('data/refill_pick.json'); lat = {p['url']: p for p in pick if p.get('region') == 'latam'}
for u, p in lat.items():
    if u in by:
        c = by[u]; r = last.get(u, {}); a = [x for x in alts(c)]
        add('P6', 'KEPUTUSAN_LATAM', 'latam_audio_spanyol', c, r.get('verdict', '?'), f"tag audio {r.get('bahasa_tag', '?')}", a, 'keputusan lo: buang atau pertahankan (alternatif non-latam tidak ada)')

rows.sort(key=lambda x: (x[0], x[1], x[4], x[3]))
hdr = ['prioritas', 'aksi', 'kelompok', 'nama', 'folder', 'negara', 'verdict_terkini', 'kategori_masalah', 'alasan', 'host', 'alt_lolos', 'alt_belum_dites', 'alt_contoh_maks3', 'butuh_dari_lo', 'url']
with open('docs/revive_kerja.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f); w.writerow(hdr); w.writerows(rows)

print(f'ditulis docs/revive_kerja.csv: {len(rows)} baris\n')
KEL = ['utama_non_hidup', 'radio_non_hidup', 'likely_dead', 'latam_audio_spanyol']
def cnt(pred): return sum(1 for r in rows if pred(r))
print('MASALAH (kenapa bermasalah) x KELOMPOK:')
print('  ' + ' | '.join(['kategori'.ljust(24)] + [k[:12].ljust(12) for k in KEL[:3]]))
for k in sorted({r[7] for r in rows if r[2] != 'latam_audio_spanyol'}, key=lambda x: -cnt(lambda r: r[7] == x and r[2] != 'latam_audio_spanyol')):
    print('  ' + ' | '.join([k.ljust(24)] + [str(cnt(lambda r: r[7] == k and r[2] == kk)).ljust(12) for kk in KEL[:3]]))
print('\nAKSI x KELOMPOK:')
print('  ' + ' | '.join(['aksi'.ljust(17)] + [k[:12].ljust(12) for k in KEL]))
for a_ in sorted({r[1] for r in rows}):
    print('  ' + ' | '.join([a_.ljust(17)] + [str(cnt(lambda r: r[1] == a_ and r[2] == k)).ljust(12) for k in KEL]))
den = cnt(lambda r: r[2] != 'latam_audio_spanyol')
tanpa = cnt(lambda r: r[2] != 'latam_audio_spanyol' and r[1] in ('SUDAH_TERCOVER', 'PROMOSI_ALT', 'TES_ALT', 'TES_ULANG_LAMBAT'))
stb = cnt(lambda r: r[1] == 'TUNGGU_STB'); link = cnt(lambda r: r[1] == 'CARI_LINK')
print(f"\nTARGET B: penyebut (utama + radio + Likely Dead) = {den} | 90% = {int(den*0.9+0.999)}")
print(f"  bisa dibereskan tanpa link baru (TERCOVER + PROMOSI_ALT + TES_ALT + TES_ULANG): {tanpa}  [TES_ALT dan TES_ULANG baru DUGAAN sampai dites]")
print(f"  tunggu STB (DRM/MPD): {stb} | wajib LINK baru (CARI_LINK): {link} (Indonesia {cnt(lambda r: r[1]=='CARI_LINK' and r[5]=='id')})")
print(f"  kalau semua DUGAAN di atas berhasil: {tanpa + stb} dari {den}; sisanya {den - tanpa - stb} bergantung link baru")
print('\nFOLDER UTAMA butuh tindakan (prioritas | aksi | nama | masalah):')
for r in rows:
    if r[2] == 'utama_non_hidup': print(f'  {r[0]} {r[1]} | {r[4][:2]} {r[3]} | {r[7]} | alt lolos={r[10]} belum={r[11]}')
print('\nLIKELY DEAD INDONESIA yang BUKAN tercover (aksi | nama | masalah):')
for r in rows:
    if r[2] == 'likely_dead' and r[5] == 'id' and r[1] != 'SUDAH_TERCOVER': print(f'  {r[1]} | {r[3]} | {r[7]}')
print('\nLIKELY DEAD CARI_LINK per negara (top 10):', collections.Counter(r[5] or '?' for r in rows if r[2] == 'likely_dead' and r[1] == 'CARI_LINK').most_common(10))
