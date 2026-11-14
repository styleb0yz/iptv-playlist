#!/usr/bin/env python3
"""EPG kecil dari i.mjh.nz dengan id iptv-org (tanpa @feed): hanya channel yang dipakai playlist, hanya acara yang belum lewat.
Per channel dipilih sumber mjh dengan jadwal terjauh. Hasilnya dipakai sebagai sumber lokal di rules.yml (epg.sources)."""
import argparse, collections, copy, gzip, json, os, re, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'iptv-playlist-builder'})
    raw = urllib.request.urlopen(req, timeout=120).read()
    return gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw


def tm(s, default):
    s = (s or '').strip()
    for f, t in (('%Y%m%d%H%M%S %z', s), ('%Y%m%d%H%M%S', s[:14])):
        try:
            d = datetime.strptime(t, f)
            return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return default


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--playlist', default='out/playlist.m3u')
    ap.add_argument('--out', required=True)
    ap.add_argument('--max-folder', type=int, default=15)
    a = ap.parse_args()
    now = datetime.now(timezone.utc)
    sites = collections.defaultdict(list)
    for x in json.loads(get('https://iptv-org.github.io/api/guides.json')):
        if x.get('channel') and x.get('site') == 'i.mjh.nz' and '#' in (x.get('site_id') or ''):
            sites[x['channel']].append(x['site_id'])
    want = {}
    for line in open(a.playlist, encoding='utf-8'):
        k = re.search(r'group-title="(\d\d)', line)
        m = re.search(r'tvg-id="([^"]+)"', line)
        if line.startswith('#EXTINF') and k and m and int(k.group(1)) <= a.max_folder:
            cid = re.sub(r'^auto\.', '', m.group(1).split('@')[0], flags=re.I)
            want.setdefault(cid, k.group(1))
    need = collections.defaultdict(list)
    for cid in want:
        for s in sites.get(cid, []):
            fl, xid = s.split('#', 1)
            need[fl].append((cid, xid))
    cand = collections.defaultdict(list)
    basi = []
    for fl, pairs in sorted(need.items()):
        try:
            src = ET.fromstring(get('https://i.mjh.nz/%s.xml' % fl))
        except Exception as e:  # noqa: BLE001
            print('GAGAL', fl, type(e).__name__)
            continue
        chan = {c.get('id'): c for c in src.findall('channel')}
        progs = collections.defaultdict(list)
        for p in src.findall('programme'):
            progs[p.get('channel')].append(p)
        suf = {}
        for i in progs:
            suf.setdefault(i.split('-')[-1], i)
        for cid, xid in pairs:
            i = xid if xid in progs else suf.get(xid.split('-')[-1])
            ps = [p for p in progs[i] if tm(p.get('stop') or p.get('start'), now) > now] if i else []
            if not ps:
                basi.append((fl, cid, xid, 'id tidak ada di file' if i is None else 'semua acara sudah lewat'))
                continue
            end = max(tm(p.get('stop') or p.get('start'), now) for p in ps)
            cand[cid].append((end, fl, chan.get(i), ps))
    tv = ET.Element('tv', {'generator-info-name': 'epg_mjh.py'})
    allp, final = [], {}
    for cid, lst in sorted(cand.items()):
        end, fl, ch, ps = max(lst, key=lambda t: t[0])
        final[cid] = (end, fl)
        c = ET.SubElement(tv, 'channel', {'id': cid})
        names = ch.findall('display-name') if ch is not None else []
        if names:
            c.append(copy.deepcopy(names[0]))
        else:
            ET.SubElement(c, 'display-name').text = cid
        for p in ps:
            q = copy.deepcopy(p)
            q.set('channel', cid)
            allp.append(q)
    tv.extend(allp)
    ET.ElementTree(tv).write(a.out, encoding='utf-8', xml_declaration=True)
    tot = collections.Counter(want.values())
    hit = collections.Counter(want[c] for c in final)
    by = collections.defaultdict(list)
    for cid, (end, fl) in final.items():
        by[fl].append((end - now).total_seconds() / 3600)
    for fl, h in sorted(by.items()):
        print('sumber %-18s %2d channel, jadwal ke depan %.0f-%.0f jam' % (fl, len(h), min(h), max(h)))
    src_c = collections.defaultdict(list)
    for cid, (end, fl) in final.items():
        src_c[fl].append(cid)
    for fl, l in sorted(src_c.items()):
        print('  ', fl, ','.join(sorted(l)))
    print('pasangan tanpa acara ke depan:', len(basi))
    for b in basi:
        print('  -', *b)
    print('dapat jadwal per folder:', {f: '%d/%d' % (hit[f], tot[f]) for f in sorted(tot)})
    print('ditulis %s: %d channel, %d acara, %d KB' % (a.out, len(final), len(allp), os.path.getsize(a.out) // 1024))


if __name__ == '__main__':
    main()
