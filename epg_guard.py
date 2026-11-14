#!/usr/bin/env python3
"""Penjaga epg_ids: tolak daftar id baru kalau jauh lebih kecil dari yang lama.
Pakai: python epg_guard.py BARU LAMA [--min-ratio 0.8]. Exit 0 = boleh dipakai, 1 = tolak."""
import os, sys


def count(p):
    if not os.path.exists(p):
        return 0
    return sum(1 for l in open(p, encoding='utf-8') if l.strip() and not l.lstrip().startswith('#'))


def main():
    a = sys.argv[1:]
    ratio = 0.8
    if '--min-ratio' in a:
        i = a.index('--min-ratio')
        ratio = float(a[i + 1])
        del a[i:i + 2]
    new, old = count(a[0]), count(a[1])
    if new == 0:
        print('GUARD: daftar id baru kosong, ditolak')
        return 1
    if old and new < old * ratio:
        print('GUARD: id baru %d < %d%% dari lama %d, ditolak (EPG kemungkinan kehilangan sumber)' % (new, int(ratio * 100), old))
        return 1
    print('GUARD: ok, id baru %d, lama %d' % (new, old))
    return 0


if __name__ == '__main__':
    sys.exit(main())
