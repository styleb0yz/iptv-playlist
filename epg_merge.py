#!/usr/bin/env python3
"""Gabung beberapa EPG XMLTV (rules.yml: epg.sources, urutan = prioritas) jadi satu file.
Satu channel id hanya diambil jadwalnya dari sumber pertama yang punya id itu.
Sumber yang gagal diunduh dilewati. Kalau semua gagal: keluar dengan kode 1 (workflow memakai epg_ids kemarin)."""
import argparse, gzip, sys, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
import yaml


def load(src):
    if src.startswith(('http://', 'https://', 'file://')):
        req = urllib.request.Request(src, headers={'User-Agent': 'iptv-playlist-builder'})
        raw = urllib.request.urlopen(req, timeout=120).read()
    else:
        raw = Path(src).read_bytes()
    if raw[:2] == b'\x1f\x8b':
        raw = gzip.decompress(raw)
    return ET.fromstring(raw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rules', default='rules.yml')
    ap.add_argument('--out', required=True)
    ap.add_argument('--source', action='append', help='timpa daftar sumber di rules.yml (boleh berulang)')
    a = ap.parse_args()
    R = yaml.safe_load(Path(a.rules).read_text(encoding='utf-8'))
    sources = a.source or R['epg'].get('sources') or [R['epg']['url']]
    chans, owner, progs, seen, ok = {}, {}, [], set(), 0
    for i, src in enumerate(sources):
        try:
            root = load(src)
        except Exception as e:  # noqa: BLE001
            print(f'WARNING sumber {i + 1} gagal ({type(e).__name__}: {str(e)[:80]}): {src}')
            continue
        ok += 1
        n_c = n_p = 0
        for c in root.findall('channel'):
            cid = c.get('id')
            if cid and cid not in chans:
                chans[cid], owner[cid] = c, i
                n_c += 1
        for p in root.findall('programme'):
            cid = p.get('channel')
            k = (cid, p.get('start'))
            if owner.get(cid) == i and k not in seen:
                seen.add(k)
                progs.append(p)
                n_p += 1
        print(f'sumber {i + 1}: +{n_c} channel baru, {n_p} acara  ({src})')
    if not ok:
        sys.exit('GAGAL: semua sumber EPG gagal diunduh.')
    tv = ET.Element('tv', {'generator-info-name': 'iptv-playlist-builder'})
    tv.extend(chans.values())
    tv.extend(progs)
    ET.ElementTree(tv).write(a.out, encoding='utf-8', xml_declaration=True)
    print(f'ditulis {a.out}: {len(chans)} channel, {len(progs)} acara dari {ok}/{len(sources)} sumber')


if __name__ == '__main__':
    main()
