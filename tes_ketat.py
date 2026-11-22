#!/usr/bin/env python3
# R2: tes ketat channel folder 01-15. BACA saja: tidak mengubah playlist atau status_lokal.json.
# Beda dengan check_local.py (yang sudah unduh segmen terakhir): di sini juga dicek
#  (1) playlist HLS live benar-benar MAJU (segmen baru muncul) atau BEKU,
#  (2) segmen terakhir dibuka ffprobe (kalau ada) untuk bukti codec video/audio asli,
#  (3) stream langsung/radio dibaca beberapa detik, dicek laju byte dan tipe isi.
# DRM tidak bisa dibuktikan: ditandai terpisah. Hasil: docs/tes_ketat.csv
import argparse, collections, csv, http.client, json, os, re, shutil, socket, subprocess, sys, tempfile, threading, time, urllib.error, urllib.parse
from concurrent.futures import ThreadPoolExecutor
import check_local as cl

FFPROBE = shutil.which('ffprobe')
GAP = 20   # jeda cek HLS live maju atau beku (detik)

def load(p):
    with open(p, encoding='utf-8') as f: return json.load(f)

def parse_pl(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    seq = 0; target = 6; end = False
    for l in lines:
        if l.startswith('#EXT-X-MEDIA-SEQUENCE:'): seq = int(re.sub(r'\D', '', l.split(':', 1)[1]) or 0)
        if l.startswith('#EXT-X-TARGETDURATION:'): target = int(re.sub(r'\D', '', l.split(':', 1)[1]) or 6)
        if l.startswith('#EXT-X-ENDLIST'): end = True
    segs = [l for l in lines if not l.startswith('#')]
    return lines, seq, target, end, segs

class NotHLS(Exception): pass
class IsDash(Exception): pass

BOM = b'\xef\xbb\xbf \r\n\t'

def fetch_pl(url, hdr, timeout):
    import urllib.request
    req = urllib.request.Request(url, headers=hdr)
    try:
        r_cm = urllib.request.urlopen(req, timeout=timeout, context=cl.CTX)
    except http.client.BadStatusLine as e:
        if 'ICY' in str(e): raise NotHLS('ICY')
        raise
    with r_cm as r:
        head = r.read(2048); h = head.lstrip(BOM)
        if h[:5] == b'<?xml' or b'<MPD' in h[:2000]: raise IsDash()
        if not h.startswith(b'#EXTM3U'): raise NotHLS(head[:120].decode('utf-8', 'replace').replace('\x00', '').replace('\n', ' '))
        return r.status, head + r.read(600_000), r.geturl()

def media_playlist(url, hdr, timeout):
    st, data, base = fetch_pl(url, hdr, timeout)
    lines, seq, target, end, segs = parse_pl(data.decode('utf-8-sig', 'replace'))
    if any(l.startswith('#EXT-X-STREAM-INF') for l in lines):
        best, best_h = None, -1
        for i, l in enumerate(lines):
            if l.startswith('#EXT-X-STREAM-INF'):
                m = re.search(r'RESOLUTION=\d+x(\d+)', l); h = int(m.group(1)) if m else 0
                nxt = next((x for x in lines[i + 1:] if not x.startswith('#')), None)
                if nxt and h >= best_h: best, best_h = nxt, h
        if not best: raise RuntimeError('master tanpa variant')
        return media_playlist(urllib.parse.urljoin(base, best), hdr, timeout)
    return lines, seq, target, end, segs, base

def probe(path):
    if not FFPROBE: return None
    try:
        o = subprocess.run([FFPROBE, '-v', 'error', '-show_entries', 'stream=codec_type,codec_name,width,height:stream_tags=language',
                            '-of', 'json', path], capture_output=True, text=True, timeout=20)
        if o.returncode != 0: return {'err': (o.stderr.strip().splitlines() or ['ffprobe gagal'])[-1][:80]}
        v = a = None; lang = ''
        for s in json.loads(o.stdout or '{}').get('streams', []):
            if s.get('codec_type') == 'video' and not v: v = f"{s.get('codec_name')} {s.get('width')}x{s.get('height')}"
            if s.get('codec_type') == 'audio' and not a:
                a = s.get('codec_name'); lang = (s.get('tags') or {}).get('language', '')
        return {'v': v or '', 'a': a or '', 'lang': lang}
    except Exception as e:  # noqa: BLE001
        return {'err': f'{type(e).__name__}'}

def test_hls(c, hdr, timeout):
    r = dict(live='', pv='', pa='', lang='')
    lines, seq1, target, end, segs1, base1 = media_playlist(c['url'], hdr, timeout)
    if not segs1: return 'MATI', 'playlist tanpa segmen', r
    if end:
        r['live'] = 'vod'
    else:
        time.sleep(min(max(target * 3, GAP), 30))
        lines, seq2, target, end, segs2, base2 = media_playlist(c['url'], hdr, timeout)
        r['live'] = 'maju' if (segs2[-1] != segs1[-1] or seq2 > seq1) else 'beku'
        segs1 = segs2; base1 = base2
    segs = segs1
    aes = any(l.startswith('#EXT-X-KEY') and 'METHOD=AES-128' in l for l in lines)
    last = None
    for s in segs[-2:]:
        last = urllib.parse.urljoin(base1, s)
        st, data, _ = cl.fetch(last, hdr, timeout, 600_000)
        if st != 200 or len(data) < 1000: return 'MATI', f'segmen http {st}, {len(data)} byte', r
    if not aes and re.search(r'\.ts(\?|$)', last) and data[:1] != b'\x47': return 'MATI', 'segmen .ts bukan 0x47', r
    if not aes:
        mp = next((l for l in lines if l.startswith('#EXT-X-MAP')), None); init = b''
        if mp:
            m = re.search(r'URI="([^"]+)"', mp)
            if m: init = cl.fetch(urllib.parse.urljoin(base1, m.group(1)), hdr, timeout, 600_000)[1]
        with tempfile.NamedTemporaryFile(suffix='.seg', delete=False) as f: f.write(init + data); p = f.name
        pr = probe(p); os.unlink(p)
        if pr is not None:
            if 'err' in pr:
                r['snip'] = f"awal={data[:8].hex()} map={'ya' if mp else 'tidak'} seg={last.split('?')[0][-24:]}"
                return 'MATI', 'ffprobe: ' + pr['err'][-50:], r
            r['pv'], r['pa'], r['lang'] = pr['v'], pr['a'], pr['lang']
            if not pr['v'] and not pr['a']: return 'MATI', 'ffprobe: tidak ada stream video/audio', r
    if r['live'] == 'beku': return 'BEKU', 'playlist tidak maju selama tes', r
    return 'HIDUP', ('AES, isi segmen tidak diprobe' if aes else ''), r

def test_icy(c, hdr, timeout, secs=4):
    u = urllib.parse.urlparse(c['url'])
    if u.scheme != 'http': return 'MATI', 'ICY lewat https tidak didukung', dict(live='', pv='', pa='', lang='')
    r = dict(live='', pv='', pa='', lang='')
    sk = socket.create_connection((u.hostname, u.port or 80), timeout=timeout)
    sk.settimeout(timeout)
    h = dict(hdr); h['Host'] = u.netloc; h['Connection'] = 'close'
    path = (u.path or '/') + ('?' + u.query if u.query else '')
    sk.sendall((f'GET {path} HTTP/1.0\r\n' + ''.join(f'{k}: {v}\r\n' for k, v in h.items()) + '\r\n').encode())
    buf = b''; t0 = time.time()
    try:
        while time.time() - t0 < secs and len(buf) < 600_000:
            b = sk.recv(8192)
            if not b: break
            buf += b
    finally:
        sk.close()
    first = buf.split(b'\r\n', 1)[0][:40].decode('latin1')
    n = len(buf) - (buf.find(b'\r\n\r\n') + 4 if b'\r\n\r\n' in buf else 0)
    if not (first.startswith('ICY 200') or ' 200' in first[:14]): return 'MATI', f'ICY status aneh: {first}', r
    if n < 12_000: return 'MATI', f'ICY cuma {n} byte dalam {secs} detik', r
    r['live'] = f'ICY {n//1024}KB/{secs}s'
    return 'HIDUP', '', r

def test_direct(c, hdr, timeout, secs=4):
    import urllib.request
    r = dict(live='', pv='', pa='', lang='')
    req = urllib.request.Request(c['url'], headers=hdr)
    t0 = time.time(); n = 0; first = b''
    try:
        resp_cm = urllib.request.urlopen(req, timeout=timeout, context=cl.CTX)
    except http.client.BadStatusLine as e:
        if 'ICY' in str(e): return test_icy(c, hdr, timeout, secs)
        raise
    with resp_cm as resp:
        ct = (resp.headers.get('Content-Type') or '').lower()
        while time.time() - t0 < secs and n < 600_000:
            b = resp.read(8192)
            if not b: break
            if not first: first = b[:120]
            n += len(b)
    r['snip'] = first.decode('utf-8', 'replace').replace('\x00', '').replace('\n', ' ')[:100] if (n < 12_000 or 'text/html' in ct) else ''
    if 'text/html' in ct: return 'MATI', 'tipe isi text/html (bukan media)', r
    if n < 12_000: return 'MATI', f'cuma {n} byte dalam {secs} detik ({ct or "tipe ?"})', r
    r['live'] = f'{n//1024}KB/{secs}s'
    return 'HIDUP', '', r

def test_dash(c, hdr, timeout, drm):
    st, data, _ = cl.fetch(c['url'], hdr, timeout, 100_000)
    ok = b'<MPD' in data[:4000]
    r = dict(live='', pv='', pa='', lang='')
    if not ok: return 'MATI', 'bukan MPD', r
    return ('DRM' if drm else 'MPD_TIDAK_DIUJI'), 'MPD terbaca' + (' (DASH di URL non-.mpd)' if not re.search(r'\.mpd(\?|$)', c['url']) else ''), r

HOSTS = {}
PER_HOST = 1
_hl = threading.Lock()
def host_sem(h):
    with _hl:
        if h not in HOSTS: HOSTS[h] = threading.Semaphore(PER_HOST)
        return HOSTS[h]

def run_one(c, timeout):
    hdr = cl.headers_for(c); host = urllib.parse.urlparse(c['url']).netloc
    drm = any('license_type' in o or 'license_key' in o for o in c.get('opts', []))
    t0 = time.time(); verdict = reason = ''; r = dict(live='', pv='', pa='', lang='')
    with host_sem(host):
        for attempt in (1, 2, 3):
            try:
                if re.search(r'\.mpd(\?|$)', c['url']):
                    verdict, reason, r = test_dash(c, hdr, timeout, drm)
                else:
                    try: verdict, reason, r = test_hls(c, hdr, timeout)
                    except IsDash: verdict, reason, r = test_dash(c, hdr, timeout, drm)
                    except NotHLS as e:
                        verdict, reason, r = test_direct(c, hdr, timeout)
                        if verdict != 'HIDUP' and not r.get('snip'): r['snip'] = str(e)[:100]
                    if drm and verdict in ('HIDUP', 'MATI', 'BEKU'): reason = f'{verdict} sebelum DRM: {reason}'.strip(); verdict = 'DRM'
                break
            except Exception as e:  # noqa: BLE001
                verdict, reason = 'MATI', f'{type(e).__name__}: {str(e)[:80]}'
                code = getattr(e, 'code', 0)
                if code == 429 and attempt < 3: time.sleep(8 * attempt); continue
                if attempt == 1 and code != 429: time.sleep(2); continue
                break
    return verdict, reason, r, int((time.time() - t0) * 1000)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--channels', default='out/channels.json'); ap.add_argument('--cands', default='out/kandidat_semua.json')
    ap.add_argument('--status', default='data/status_lokal.json'); ap.add_argument('--out', default='docs/tes_ketat.csv')
    ap.add_argument('--workers', type=int, default=8); ap.add_argument('--timeout', type=float, default=12)
    ap.add_argument('--per-host', type=int, default=2); ap.add_argument('--gap', type=float, default=12)
    ap.add_argument('--only-from', default='', help='CSV hasil sebelumnya: tes ulang hanya URL yang verdict-nya bukan HIDUP, lalu tampilkan angka gabungan')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--urls-file', default='', help='file berisi URL (satu per baris): tes persis URL ini, di folder mana pun')
    a = ap.parse_args()
    PER_HOST = a.per_host; GAP = a.gap
    ch = load(a.channels); ks = {c['url']: c for c in load(a.cands)}; st = load(a.status)
    tg = [c for c in ch if re.match(r'(0\d|1[0-5])\b', c['folder'])]
    if a.urls_file:
        want = set(l.strip() for l in open(a.urls_file, encoding='utf-8') if l.strip()); tg = [c for c in ch if c['url'] in want]
    old = {}
    if a.only_from:
        for r0 in csv.DictReader(open(a.only_from, encoding='utf-8-sig')): old[r0['url']] = r0
        tg_all = tg
        tg = [c for c in tg if old.get(c['url'], {}).get('verdict', 'HIDUP') != 'HIDUP']
    if a.limit: tg = tg[:a.limit]
    print(f'target {len(tg)} channel | ffprobe: {FFPROBE or "TIDAK ADA"} | workers {a.workers} | per-host {PER_HOST} | gap {GAP}s', flush=True)
    res = [None] * len(tg); done = [0]
    def job(i):
        c = dict(ks.get(tg[i]['url'], {})); c['url'] = tg[i]['url']
        res[i] = run_one(c, a.timeout); done[0] += 1
        if done[0] % 10 == 0: print(f'  ...{done[0]}/{len(tg)}', flush=True)
    with ThreadPoolExecutor(a.workers) as ex: list(ex.map(job, range(len(tg))))
    rows = []
    for c, (v, why, r, ms) in zip(tg, res):
        s = st.get(c['url']); o = 'belum_dites' if s is None else ('lolos' if s.get('ok') else 'gagal')
        rows.append([c['name'], c['folder'], c['src'], o, v, why, r['live'], r['pv'], r['pa'], r['lang'], ms, c['url'], r.get('snip', ''), old.get(c['url'], {}).get('verdict', '')])
    with open(a.out, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f); w.writerow(['nama', 'folder', 'sumber', 'tes_lokal_lama', 'verdict', 'alasan', 'live_atau_laju', 'video', 'audio', 'bahasa_tag', 'ms', 'url', 'cuplikan', 'verdict_r2']); w.writerows(rows)
    print(f'\nditulis {a.out}: {len(rows)} baris')
    print('verdict baru:', dict(collections.Counter(r[4] for r in rows)))
    if a.only_from:
        print('perubahan dari R2 (nama | R2 -> baru | alasan):')
        for r in rows:
            if r[4] != r[13] and not r[1].startswith('15'): print(f'  {r[1][:2]} {r[0]} | {r[13]} -> {r[4]} | {r[5][:60]}')
        newv = {r[11]: r[4] for r in rows}
        final = [(c, newv.get(c['url'], old.get(c['url'], {}).get('verdict', 'HIDUP'))) for c in tg_all]
    else:
        final = [(c, r[4]) for c, r in zip(tg, rows)]
    nr = [x for x in final if not x[0]['folder'].startswith('15')]; rd = [x for x in final if x[0]['folder'].startswith('15')]
    print('\nANGKA GABUNGAN' if a.only_from else '\nANGKA')
    for nm, g in (('Folder utama tanpa radio', nr), ('Radio', rd)):
        if not g: continue
        h = sum(1 for _, v in g if v == 'HIDUP'); d = sum(1 for _, v in g if v in ('DRM', 'MPD_TIDAK_DIUJI'))
        print(f'{nm}: {len(g)} | HIDUP {h} = {100*h/len(g):.1f}% | DRM/MPD {d} | HIDUP+DRM/MPD {100*(h+d)/len(g):.1f}%')
    print('\nMASIH BUKAN HIDUP (utama): folder nama | verdict | alasan | cuplikan')
    rowby = {r[11]: r for r in rows}
    for c, v in nr:
        if v != 'HIDUP':
            r = rowby.get(c['url']); print(f"  {c['folder'][:2]} {c['name']} | {v} | {(r[5][:60] if r else 'tidak dites ulang')} | {(r[12][:60] if r else '')}")
    print('\nRadio masih bukan HIDUP:', sum(1 for _, v in rd if v != 'HIDUP'))
