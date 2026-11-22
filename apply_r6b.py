import csv, glob, json, os, re
base = os.path.expanduser('~/iptv_stb_privat')
rows = [r for r in csv.DictReader(open(base + '/tes_kandidat_semua.csv', encoding='utf-8')) if r['status'] == 'HIDUP_LOKAL']
ent = {}
for p in glob.glob(base + '/*.m3u') + glob.glob(base + '/serve/*.m3u'):
    cur = None
    for l in open(p, encoding='utf-8', errors='ignore').read().splitlines():
        l = l.strip()
        if l.startswith('#EXTINF'):
            cur = {'extinf': l, 'opts': []}
        elif cur is not None and l.startswith(('#EXTVLCOPT', '#EXTHTTP')):
            cur['opts'].append(l)
        elif cur is not None and l and not l.startswith('#'):
            ent.setdefault(l, cur)
            cur = None
specs = [
    ('RCTI HD', 'RCTI.id@HD', ['RCTI HD', 'RCTI HD (1080p)']),
    ('ANTV (Indonesia)', 'ANTV.id@SD', ['ANTV (Indonesia)', 'ANTV (Indonesia) (720p)']),
    ('GTV (Indonesia) HD', 'GTV.id@HD', ['GTV (Indonesia) HD', 'GTV (Indonesia) HD (1080p)']),
    ('MNCTV', 'MNCTV.id@SD', ['MNCTV']),
    ('Trans7', 'Trans7.id@SD', ['Trans7']),
    ('Fox News Channel', 'FoxNewsChannel.us@SD', ['Fox News Channel']),
    ('GREAT! movies', 'GREATmovies.uk@UK', ['GREAT! movies']),
    ('RT HD', 'RT.ru@HD', ['RT HD', 'RT (720p)']),
    ('History (United States)', 'History.us@East', ['History (United States)', 'History (Brazil) (720p)']),
    ('Nick Jr. (United States)', 'NickJr.us@East', ['Nick Jr. (United States)', 'Nick Jr. (India) (576p)']),
    ('CBeebies (United Kingdom) HD', 'CBeebies.uk@HD', ['CBeebies (United Kingdom) HD']),
    ('Celestial Movies (576i)', 'CelestialMovies.hk@SD', ['Celestial Movies (576i)']),
]
lp = 'data/extra/links_user.m3u'
exist = set(l.strip() for l in open(lp, encoding='utf-8').read().splitlines() if l.strip() and not l.startswith('#'))
out = ['# R6b (16 Nov): 12 channel dari aktv dan gvision, identitas dicek user (frame).']
picks = json.load(open('data/refill_pick.json', encoding='utf-8'))
pu = set(p['url'] for p in picks)
for nama, tid, names in specs:
    c = sorted([r for r in rows if r['nama'] in names and r['url'] in ent], key=lambda r: r['sumber'] != 'aktv_1.m3u')
    c = [r for r in c if r['url'] not in exist]
    if not c:
        print(nama, '| TIDAK ADA kandidat baru, dilewati')
        continue
    r = c[0]
    e = ent[r['url']]
    m = re.search(r'tvg-logo="([^"]*)"', e['extinf'])
    out.append('#EXTINF:-1 tvg-id="%s" tvg-logo="%s" group-title="General",%s' % (tid, m.group(1) if m else '', nama))
    out += e['opts']
    out.append(r['url'])
    exist.add(r['url'])
    print(nama, '| ditambah dari', r['sumber'], '| opsi header', len(e['opts']))
    if nama.startswith('Celestial') and r['url'] not in pu:
        picks.append({'brand': 'Celestial Movies', 'label': 'Celestial Movies', 'folder': 'movies', 'pos': 320, 'url': r['url'], 'region': 'id', 'src_name': 'Celestial Movies (aktv)', 'height': 0})
        print('Celestial Movies | pick movies ditambah')
open(lp, 'a', encoding='utf-8').write('\n'.join(out) + '\n')
json.dump(picks, open('data/refill_pick.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('selesai. entri links_user ditambah:', sum(1 for x in out if x.startswith('#EXTINF')))
