#!/usr/bin/env python3
"""Buat data/epg_map.json: {file_epg_mjh: {id_di_xml: id_iptv_org}}.
Hanya channel playlist folder 01-15 yang punya site i.mjh.nz di guides.json DAN id-nya punya acara di file XML-nya."""
import collections, gzip, json, re, sys, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'iptv-playlist-builder'})
    raw = urllib.request.urlopen(req, timeout=120).read()
    return gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw

playlist = sys.argv[1] if len(sys.argv) > 1 else 'out/playlist.m3u'
sites = collections.defaultdict(list)
for x in json.loads(get('https://iptv-org.github.io/api/guides.json')):
    if x.get('channel') and x.get('site') == 'i.mjh.nz' and '#' in x.get('site_id', ''):
        sites[x['channel']].append(x['site_id'])
want = {}
for line in open(playlist, encoding='utf-8'):
    if not line.startswith('#EXTINF'):
        continue
    k = re.search(r'group-title="(\d\d)', line)
    m = re.search(r'tvg-id="([^"]+)"', line)
    if k and m and int(k.group(1)) <= 15:
        want.setdefault(m.group(1).split('@')[0], k.group(1))
need = collections.defaultdict(list)
for cid in want:
    for s in sites.get(cid, []):
        fl, xid = s.split('#', 1)
        need[fl].append((cid, xid))
res, covered = {}, {}
for fl, pairs in sorted(need.items()):
    try:
        raw = get('https://i.mjh.nz/%s.xml' % fl)
    except Exception as e:
        print('GAGAL', fl, type(e).__name__)
        continue
    have = {i.decode() for i in re.findall(rb'<programme[^>]*\bchannel="([^"]*)"', raw)}
    if not have:
        print('KOSONG', fl, len(raw), 'bytes')
        continue
    stops = re.findall(rb'stop="(\d{12})', raw)
    stop = max(stops).decode() if stops else '-'
    m = {}
    for cid, xid in pairs:
        for cand in (xid, xid.split('-')[-1]):
            if cand in have:
                m[cand] = cid
                covered.setdefault(cid, fl)
                break
    res[fl] = m
    print('OK', fl, '%d dipetakan dari %d, jadwal sampai %s' % (len(m), len(pairs), stop))
tot = collections.Counter(want.values())
hit = collections.Counter(want[c] for c in covered)
print('id unik per folder (dapat jadwal/total):', {f: '%d/%d' % (hit[f], tot[f]) for f in sorted(tot)})
json.dump(res, open('data/epg_map.json', 'w'), indent=1, sort_keys=True)
print('ditulis data/epg_map.json:', sum(len(v) for v in res.values()), 'pasangan,', len(covered), 'channel iptv-org')
