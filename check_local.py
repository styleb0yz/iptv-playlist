#!/usr/bin/env python3
"""Cek stream dari jaringan LO (MyRepublic). Hanya pustaka standar Python 3.8+.

  python build.py ...                      # hasilkan out/kandidat_cek.json
  python check_local.py out/kandidat_cek.json -o status_lokal.json
  python build.py ...                      # build ulang, sekarang pemenang ditentukan hasil tes

PENTING: jangan ganti DNS komputer ke 8.8.8.8 / 1.1.1.1. Stream dens.tv butuh DNS ISP
(MyRepublic). Script ini memakai resolver sistem, jadi jalankan di perangkat yang DNS-nya bawaan ISP.

Yang dianggap OK: playlist HLS terbaca, ada segmen, dan segmen terakhir benar-benar bisa diunduh
(ukuran > 1 KB; kalau .ts, byte pertama 0x47). Ini menangkap kasus 404 dan layar hitam karena
segmen kosong. Yang TIDAK bisa dibuktikan script: DRM (entri KODIPROP widevine ditandai drm=true),
kualitas gambar, atau stream yang cuma jalan pada player tertentu.
Format status_lokal.json: {url: {"ok": bool, "height": int, "ms": int, "reason": str, "drm": bool, "checked": iso}}
"""
import argparse, json, re, ssl, sys, threading, time, urllib.parse, urllib.request
import zlib
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

UA_DEFAULT = 'Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36 TiviMate-check'


def headers_for(c):
    h = {'User-Agent': UA_DEFAULT}
    a = c.get('attrs', {})
    if a.get('http-user-agent'): h['User-Agent'] = a['http-user-agent']
    if a.get('http-referrer'): h['Referer'] = a['http-referrer']
    for o in c.get('opts', []):
        m = re.match(r'#EXTVLCOPT:http-(user-agent|referrer|origin)=(.*)', o, re.I)
        if m:
            k = {'user-agent': 'User-Agent', 'referrer': 'Referer', 'origin': 'Origin'}[m.group(1).lower()]
            h[k] = m.group(2).strip()
        elif o.startswith('#EXTHTTP:'):
            try:
                for k, v in json.loads(o.split(':', 1)[1]).items():
                    h[{'referer': 'Referer', 'origin': 'Origin', 'user-agent': 'User-Agent'}.get(k.lower(), k)] = str(v)
            except ValueError:
                pass
    return h


def fetch(url, hdr, timeout, limit):
    req = urllib.request.Request(url, headers=hdr)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        data = r.read(limit)
        if data[:2] == b'\x1f\x8b':
            data = zlib.decompressobj(31).decompress(data)
        return r.status, data, r.geturl()


def check_one(c, timeout):
    url, hdr, t0 = c['url'], headers_for(c), time.time()
    drm = any('license_type' in o or 'license_key' in o for o in c.get('opts', []))
    res = dict(ok=False, height=0, reason='', drm=drm)
    try:
        st, data, final = fetch(url, hdr, timeout, 600_000)
        if st != 200:
            res['reason'] = f'http {st}'
        elif re.search(r'\.mpd(\?|$)', final) or data.lstrip()[:6] in (b'<?xml ', b'<MPD x'):
            res['ok'] = b'<MPD' in data[:4000]
            res['reason'] = '' if res['ok'] else 'bukan MPD'
        elif data.lstrip().startswith(b'#EXTM3U'):
            res.update(check_hls(data.decode('utf-8', 'replace'), final, hdr, timeout))
        else:  # stream langsung (ts/aac/mp3/icecast): cukup ada byte yang mengalir
            res['ok'] = len(data) > 1000
            res['reason'] = '' if res['ok'] else f'data cuma {len(data)} byte'
    except Exception as e:  # noqa: BLE001
        res['reason'] = f'{type(e).__name__}: {str(e)[:80]}'
    res['ms'] = int((time.time() - t0) * 1000)
    res['checked'] = datetime.now(timezone.utc).isoformat(timespec='seconds')
    return res


def check_hls(text, base, hdr, timeout):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    height = 0
    if any(l.startswith('#EXT-X-STREAM-INF') for l in lines):
        best, best_h = None, -1
        for i, l in enumerate(lines):
            if l.startswith('#EXT-X-STREAM-INF'):
                m = re.search(r'RESOLUTION=\d+x(\d+)', l)
                h = int(m.group(1)) if m else 0
                nxt = next((x for x in lines[i + 1:] if not x.startswith('#')), None)
                if nxt and h >= best_h:
                    best, best_h = nxt, h
        if not best:
            return dict(ok=False, reason='master tanpa variant')
        height = max(best_h, 0)
        st, data, base = fetch(urllib.parse.urljoin(base, best), hdr, timeout, 600_000)
        if st != 200 or not data.lstrip().startswith(b'#EXTM3U'):
            return dict(ok=False, height=height, reason=f'media playlist http {st}')
        lines = [l.strip() for l in data.decode('utf-8', 'replace').splitlines() if l.strip()]
    segs = [l for l in lines if not l.startswith('#')]
    if not segs:
        return dict(ok=False, height=height, reason='playlist tanpa segmen')
    seg = urllib.parse.urljoin(base, segs[-1])
    st, data, _ = fetch(seg, hdr, timeout, 65_536)
    if st != 200 or len(data) < 1000:
        return dict(ok=False, height=height, reason=f'segmen http {st}, {len(data)} byte')
    keyl = next((l for l in lines if l.startswith('#EXT-X-KEY') and 'METHOD=AES-128' in l), None)
    if keyl:  # segmen terenkripsi: byte awal acak, jadi cek kunci 16 byte saja
        m = re.search(r'URI="([^"]+)"', keyl)
        if m:
            try:
                st, key, _ = fetch(urllib.parse.urljoin(base, m.group(1)), hdr, timeout, 64)
            except Exception as e:  # noqa: BLE001
                return dict(ok=False, height=height, reason=f'kunci AES: {type(e).__name__}')
            if st != 200 or len(key) != 16:
                return dict(ok=False, height=height, reason=f'kunci AES tidak valid ({len(key)} byte)')
    elif re.search(r'\.ts(\?|$)', seg) and data[:1] != b'\x47':
        return dict(ok=False, height=height, reason='segmen .ts tidak valid (bukan 0x47)')
    return dict(ok=True, height=height, reason='')


CTX = ssl.create_default_context()

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('kandidat')
    ap.add_argument('-o', '--out', default='status_lokal.json')
    ap.add_argument('--workers', type=int, default=16)
    ap.add_argument('--per-host', type=int, default=4, help='maks koneksi bersamaan per host')
    ap.add_argument('--timeout', type=float, default=10)
    ap.add_argument('--retries', type=int, default=2)
    ap.add_argument('--max-age-hours', type=float, default=24, help='lewati URL yang dites lebih baru dari ini')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--skip-exempt', action='store_true', help='mode GitHub: lewati channel negara exempt + [Geo-blocked]')
    ap.add_argument('--exempt-countries', default='id')
    ap.add_argument('--max-minutes', type=float, default=0, help='batas waktu total (0 = tanpa batas); sisanya dilewati')
    ap.add_argument('--max-fail-rate', type=float, default=0, help='kalau gagal > rasio ini, jangan simpan (mis. 0.7): tanda jaringan runner bermasalah')
    ap.add_argument('--insecure', action='store_true', help='abaikan sertifikat SSL rusak (player bisa saja menolaknya)')
    a = ap.parse_args()
    if a.insecure:
        CTX.check_hostname, CTX.verify_mode = False, ssl.CERT_NONE

    cands = json.load(open(a.kandidat, encoding='utf-8'))
    try:
        status = json.load(open(a.out, encoding='utf-8'))
    except (OSError, ValueError):
        status = {}
    cutoff = datetime.now(timezone.utc) - timedelta(hours=a.max_age_hours)
    todo = []
    ex = set(a.exempt_countries.split(','))
    if a.skip_exempt:
        n0 = len(cands)
        cands = [c for c in cands if c.get('country') not in ex and not c.get('geo')]
        print(f'mode GitHub: {n0 - len(cands)} entri exempt (negara {sorted(ex)} / geo-blocked) dilewati')
    for c in cands:
        s = status.get(c['url'])
        fresh = s and datetime.fromisoformat(s['checked']) > cutoff
        if a.force or not fresh:
            todo.append(c)
    print(f'{len(cands)} kandidat, {len(todo)} dites, {len(cands) - len(todo)} dilewati (masih baru)')

    locks = defaultdict(lambda: threading.Semaphore(a.per_host))
    lk = threading.Lock()

    deadline = time.time() + a.max_minutes * 60 if a.max_minutes else None
    skipped = [0]

    def job(c):
        host = urllib.parse.urlparse(c['url']).netloc
        with locks[host]:
            if deadline and time.time() > deadline:
                skipped[0] += 1
                return c, None
            r = None
            for _ in range(a.retries):
                r = check_one(c, a.timeout)
                if r['ok']:
                    break
        return c, r

    ok = bad = 0
    new_prev = dict(status)
    with ThreadPoolExecutor(a.workers) as ex:
        futs = [ex.submit(job, c) for c in todo]
        for n, f in enumerate(as_completed(futs), 1):
            c, r = f.result()
            if r is None:
                continue
            prev = new_prev.get(c['url'], {})
            r['fails'] = 0 if r['ok'] else (prev.get('fails', 0) + 1 if prev.get('ok') is False else 1)
            with lk:
                status[c['url']] = r
            ok += r['ok']; bad += not r['ok']
            if not r['ok']:
                print(f'  GAGAL  {c["name"][:40]:40s} {r["reason"]}')
            if n % 50 == 0 and not a.max_fail_rate:
                json.dump(status, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
                print(f'  ...{n}/{len(todo)}')
    if a.max_fail_rate and (ok + bad) >= 50 and bad / (ok + bad) > a.max_fail_rate:
        print(f'DIBATALKAN: {bad}/{ok + bad} gagal (> {a.max_fail_rate:.0%}). Kemungkinan jaringan runner bermasalah, '
              f'hasil TIDAK disimpan ({a.out} tetap versi lama).')
        sys.exit(3)
    json.dump(status, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(f'selesai: {ok} OK, {bad} gagal, {skipped[0]} dilewati (batas waktu) -> {a.out}')
    drm_ok = sum(1 for c in cands if status.get(c['url'], {}).get('drm') and status[c['url']]['ok'])
    if drm_ok:
        print(f'catatan: {drm_ok} stream OK berstatus DRM, playlist/segmen terbaca tapi belum tentu bisa diputar di TiviMate')
