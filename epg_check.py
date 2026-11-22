#!/usr/bin/env python3
"""Cek EPG XMLTV terhadap playlist.m3u hasil build.py.

Pakai:
  python epg_check.py --epg epg.xml --playlist playlist.m3u
  (epg boleh .xml atau .xml.gz; kalau --epg berupa URL, diunduh dulu)

Output:
  epg_ids.txt   id channel yang punya jadwal (dibaca build.py mode 'single')
  ringkasan di layar (salin dan kirim ke Claude)
"""
import argparse, gzip, io, re, sys, urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone


def open_epg(src):
    if re.match(r'https?://', src):
        data = urllib.request.urlopen(src, timeout=60).read()
        print(f'Diunduh {len(data)/1e6:.1f} MB dari {src}')
    else:
        data = open(src, 'rb').read()
    if data[:2] == b'\x1f\x8b':
        data = gzip.decompress(data)
    return io.BytesIO(data)


def parse_time(s):
    s = s.strip()
    m = re.match(r'(\d{14})\s*([+-]\d{4})?', s)
    if not m:
        return None
    dt = datetime.strptime(m.group(1), '%Y%m%d%H%M%S')
    tz = m.group(2) or '+0000'
    sign = 1 if tz[0] == '+' else -1
    off = sign * (int(tz[1:3]) * 60 + int(tz[3:5]))
    return dt.replace(tzinfo=timezone.utc).timestamp() - off * 60


def norm(i):
    return re.sub(r'^auto\.', '', i.split('@')[0], flags=re.I).lower()


def read_epg(f):
    chans, progs, tmin, tmax = set(), defaultdict(int), None, None
    for _, el in ET.iterparse(f, events=('end',)):
        if el.tag == 'channel':
            chans.add(el.get('id', ''))
        elif el.tag == 'programme':
            cid = el.get('channel', '')
            progs[cid] += 1
            for k in ('start', 'stop'):
                t = parse_time(el.get(k, ''))
                if t:
                    tmin = t if tmin is None else min(tmin, t)
                    tmax = t if tmax is None else max(tmax, t)
        else:
            continue
        el.clear()
    return chans, progs, tmin, tmax


def read_playlist(path):
    rows = []
    for line in open(path, encoding='utf-8', errors='replace'):
        if line.startswith('#EXTINF'):
            tvg = re.search(r'tvg-id="([^"]*)"', line)
            grp = re.search(r'group-title="([^"]*)"', line)
            name = line.rsplit(',', 1)[-1].strip()
            rows.append((grp.group(1) if grp else '?', tvg.group(1) if tvg else '', name))
    return rows


def fmt(t):
    return datetime.fromtimestamp(t, timezone.utc).strftime('%Y-%m-%d %H:%M UTC') if t else '-'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--epg', required=True)
    ap.add_argument('--playlist', default=None, help='opsional: kalau diisi, tampilkan cakupan per folder')
    ap.add_argument('--out', default='epg_ids.txt')
    a = ap.parse_args()

    chans, progs, tmin, tmax = read_epg(open_epg(a.epg))
    with_prog = {c for c in chans | set(progs) if progs.get(c)}
    print(f'\nEPG: {len(chans)} channel, {len(with_prog)} punya jadwal, {sum(progs.values())} acara')
    print(f'Jadwal: {fmt(tmin)} sampai {fmt(tmax)}')
    now = datetime.now(timezone.utc).timestamp()
    if tmax and tmax < now:
        print('PERINGATAN: jadwal terakhir sudah lewat, EPG basi.')
    elif tmax:
        print(f'Sisa jadwal ke depan: {(tmax-now)/86400:.1f} hari')

    with open(a.out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sorted(with_prog)) + '\n')
    print(f'Ditulis {a.out} ({len(with_prog)} id)')

    if not a.playlist:
        return 0

    exact_set = with_prog
    norm_map = defaultdict(set)
    for c in with_prog:
        norm_map[norm(c)].add(c)

    pl = read_playlist(a.playlist)
    order = list(dict.fromkeys(g for g, _, _ in pl))
    essential = set(order[:15])
    per = defaultdict(lambda: [0, 0, 0])  # total, exact, normalized
    miss = defaultdict(list)
    for grp, tvg, name in pl:
        per[grp][0] += 1
        if tvg and tvg in exact_set:
            per[grp][1] += 1
            per[grp][2] += 1
        elif tvg and norm(tvg) in norm_map:
            per[grp][2] += 1
        elif len(miss[grp]) < 5:
            miss[grp].append(name)

    tot = sum(v[0] for v in per.values())
    ex = sum(v[1] for v in per.values())
    nm = sum(v[2] for v in per.values())
    print(f'\nCakupan playlist ({tot} entri): id persis {ex} ({ex*100//max(tot,1)}%), '
          f'setelah normalisasi/remap {nm} ({nm*100//max(tot,1)}%)\n')
    print(f'{"Folder":50} {"total":>6} {"persis":>7} {"remap":>6}')
    for g in order:
        t, e, n = per[g]
        if g in essential or n:   # folder esensial selalu, arsip hanya yang ada isinya
            print(f'{g[:50]:50} {t:6} {e:7} {n:6}')
    print('\nContoh channel esensial tanpa jadwal (maks 5 per folder):')
    for g in order:
        if g in essential and miss[g]:
            print(f'  {g[:40]}: {", ".join(miss[g])}')


if __name__ == '__main__':
    sys.exit(main())
