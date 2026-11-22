#!/usr/bin/env python3
# R3d: cari link .m3u8/.mpd dari halaman resmi channel. BACA saja, tidak mengubah playlist.
# Input: data/situs_scrape.txt, satu baris:  Nama Channel | https://halaman-resmi/
# Sopan: patuh robots.txt, 1 detik antar request ke host sama, maksimal 8 halaman dan 8 file JS per situs.
# Tidak menembus login, DRM, atau proteksi lain: kalau ketemu, dilaporkan dan dilewati.
# Output: docs/scrape_hasil.csv (semua kandidat + hasil tes) dan docs/scrape_siap.txt (siap ditempel ke data/links_user.txt).
import csv, html, re, sys, time, threading, urllib.parse, urllib.request, urllib.robotparser, collections
import check_local as cl
import tes_ketat as tk

tk.GAP = 12; tk.PER_HOST = 1
UA = cl.UA_DEFAULT
LAST = collections.defaultdict(float); LK = threading.Lock()

def get(url, ref='', limit=1_500_000, timeout=15):
    host = urllib.parse.urlparse(url).netloc
    with LK:
        w = LAST[host] + 1.0 - time.time(); LAST[host] = max(time.time(), LAST[host]) + (1.0 if w > 0 else 0)
    if w > 0: time.sleep(w)
    h = {'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml,application/javascript,*/*'}
    if ref: h['Referer'] = ref
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout, context=cl.CTX) as r:
        return r.status, r.read(limit).decode('utf-8', 'replace'), r.geturl()

def robots_ok(url):
    p = urllib.parse.urlparse(url)
    try:
        st, body, _ = get(f'{p.scheme}://{p.netloc}/robots.txt', limit=200_000, timeout=8)
        if st != 200: return True
        rp = urllib.robotparser.RobotFileParser(); rp.parse(body.splitlines())
        return rp.can_fetch('*', url)
    except Exception:  # noqa: BLE001
        return True

M3U = re.compile(r'''https?:(?:\\?/){2}(?:[^\s"'<>\\]|\\/)+?\.(?:m3u8|mpd)(?:\?[^\s"'<>\\]*)?|(?<=["'])/(?:[^\s"'<>\\]|\\/)+?\.(?:m3u8|mpd)(?:\?[^\s"'<>\\]*)?''', re.I)
def clean(u, base):
    u = html.unescape(u.replace('\\/', '/').replace('\\u0026', '&').replace('\\u002F', '/'))
    return urllib.parse.urljoin(base, u)
def find_media(text, base):
    return [clean(m.group(0), base) for m in M3U.finditer(text)]
LINKRE = re.compile(r'''(?:href|src)=["']([^"']+)["']''', re.I)
KEY = re.compile(r'live|stream|siaran|tv|watch|nonton|player', re.I)
def cred(u):
    p = urllib.parse.urlparse(u)
    if p.username or p.password or re.search(r'(^|[?&])(user|username|pass|password|pwd|login)=', p.query, re.I): return 'KERAS'
    if re.search(r'/[^/]+/[^/]+/\d+(\.\w+)?$', p.path): return 'LUNAK'
    return ''

def scrape_site(nama, page):
    out = []; seen_pages = set(); notes = []
    if not robots_ok(page): return [], ['robots.txt melarang']
    queue = [page]; js = []; host = urllib.parse.urlparse(page).netloc; drm = False
    while queue and len(seen_pages) < 8:
        u = queue.pop(0)
        if u in seen_pages: continue
        seen_pages.add(u)
        try: st, body, final = get(u)
        except Exception as e:  # noqa: BLE001
            notes.append(f'{u[:60]} gagal: {type(e).__name__}'); continue
        if re.search(r'widevine|playready|license_?url|drm', body, re.I): drm = True
        out += [(c, u) for c in find_media(body, final)]
        for l in LINKRE.findall(body):
            full = urllib.parse.urljoin(final, l); pu = urllib.parse.urlparse(full)
            if l.lower().split('?')[0].endswith('.js') and len(js) < 8 and full not in js: js.append(full)
            elif pu.netloc == host and KEY.search(pu.path) and full not in seen_pages and len(queue) < 8 and not re.search(r'\.(png|jpe?g|gif|svg|css|ico|webp)$', pu.path, re.I): queue.append(full)
    for j in js:
        try: st, body, final = get(j, ref=page)
        except Exception: continue  # noqa: BLE001
        out += [(c, j) for c in find_media(body, final)]
        if re.search(r'widevine|playready|license_?url', body, re.I): drm = True
    if drm: notes.append('ada tanda DRM/lisensi di halaman')
    uniq = []
    for c, src in out:
        if c not in [x[0] for x in uniq]: uniq.append((c, src))
    if not uniq: notes.append('tidak ada URL m3u8/mpd di HTML/JS (mungkin dimuat lewat API/JS dinamis)')
    return uniq, notes

def main():
    items = []
    for ln in open('data/situs_scrape.txt', encoding='utf-8'):
        ln = ln.strip()
        if not ln or ln.startswith('#'): continue
        p = [x.strip() for x in ln.split('|')]
        if len(p) < 2 or not p[1].startswith('http'): print('dilewati:', ln[:70]); continue
        items.append((p[0], p[1]))
    print(f'{len(items)} situs | ffprobe: {tk.FFPROBE or "TIDAK ADA"}', flush=True)
    rows = []; siap = []
    for nama, page in items:
        cands, notes = scrape_site(nama, page)
        print(f'- {nama}: {len(cands)} kandidat | {"; ".join(notes) or "ok"}', flush=True)
        if not cands: rows.append([nama, page, '', '', '', '', '', '', '', '', '; '.join(notes)]); continue
        for c, src in cands[:5]:
            v, why, r, ms = tk.run_one({'url': c, 'opts': [], 'attrs': {'http-referrer': page}}, 12)
            ref = ''
            if v == 'HIDUP':
                v2, _, _, _ = tk.run_one({'url': c, 'opts': [], 'attrs': {}}, 12)
                ref = 'tidak' if v2 == 'HIDUP' else 'YA (butuh Referer = halaman resmi)'
            tok = 'bertoken (bisa kedaluwarsa)' if re.search(r'(^|[?&])(token|expires?|exp|sig|signature|hdnts|auth)=', c, re.I) else ''
            cr = cred(c)
            rows.append([nama, page, c, v, why, r['pv'], r['pa'] + ('/' + r['lang'] if r['lang'] else ''), ref, tok, cr, '; '.join(notes)])
            if v == 'HIDUP' and cr != 'KERAS': siap.append(f'{nama} | {c} | scrape:{urllib.parse.urlparse(page).netloc}' + (' | butuh-referer' if ref.startswith('YA') else '') + (' | bertoken' if tok else '') + (' | cek-drm' if any('DRM' in n for n in notes) else ''))
    with open('docs/scrape_hasil.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f); w.writerow(['nama', 'halaman', 'kandidat_url', 'verdict', 'alasan', 'video', 'audio_bahasa', 'butuh_referer', 'token', 'kredensial', 'catatan']); w.writerows(rows)
    open('docs/scrape_siap.txt', 'w', encoding='utf-8').write('\n'.join(siap) + ('\n' if siap else ''))
    print(f'\nditulis docs/scrape_hasil.csv ({len(rows)} baris) dan docs/scrape_siap.txt ({len(siap)} link HIDUP)')
    print('\nHIDUP (nama | video | audio | referer | token):')
    for r in rows:
        if r[3] == 'HIDUP': print(f'  {r[0]} | {r[5]} | {r[6]} | {r[7]} | {r[8] or "-"} | {r[2][:80]}')
    print('\nTidak berhasil (nama | alasan):')
    for r in rows:
        if r[3] != 'HIDUP' and not any(x[3] == 'HIDUP' and x[0] == r[0] for x in rows): print(f'  {r[0]} | {r[3] or "-"} | {(r[4] or r[10])[:70]}')

main()
