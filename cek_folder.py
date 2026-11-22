import csv, re, collections

rows = [r for r in csv.DictReader(open('docs/revive_status_1511.csv', encoding='utf-8-sig')) if not r['status_baru'].startswith('AMAN')]
pl = collections.defaultdict(list)
for l in open('out/playlist.m3u', encoding='utf-8', errors='replace'):
    if l.startswith('#EXTINF'):
        a = dict(re.findall(r'([\w-]+)="([^"]*)"', l))
        nm = l.split(',', 1)[1].strip()
        pl[re.sub(r'[^a-z0-9]+', '', re.sub(r'\[[^\]]*\]|\([^)]*\)', ' ', nm.lower()))].append(a.get('group-title', ''))
main = no = 0
hilang = []
for r in rows:
    k = re.sub(r'[^a-z0-9]+', '', re.sub(r'\[[^\]]*\]|\([^)]*\)', ' ', r['nama'].lower()))
    if [x for x in pl.get(k, []) if not x.startswith('Archive')]:
        main += 1
    else:
        no += 1
        hilang.append(r['nama'][:30])
print('non-aman %d: di folder utama %d | belum di folder utama %d' % (len(rows), main, no))
print('belum di folder utama:', ', '.join(hilang))
