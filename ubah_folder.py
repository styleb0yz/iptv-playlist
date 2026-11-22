import re, shutil, yaml

shutil.copy('rules.yml', 'rules.yml.bak_v112s')
L = open('rules.yml', encoding='utf-8').read().split('\n')
i0 = next(i for i, l in enumerate(L) if l.startswith('folders:')) + 1
i1 = i0
while L[i1].lstrip().startswith('- {key:'):
    i1 += 1
blok = L[i0:i1]
NAMA = {
 'national': 'Indonesia National TV', 'news': 'Indonesia News', 'islam': 'Islamic TV (Indonesia & Haramain)',
 'sports': 'Football & Sports', 'sports2': 'More Sports (NBA, Golf, Rugby)', 'movies': 'Movies & Series',
 'docs': 'Documentary & Science', 'intl_news': 'International News', 'kids': 'Kids & Cartoons',
 'america': 'USA TV & Cable', 'uk': 'UK TV', 'europe': 'Europe TV', 'music': 'Music',
 'tvri': 'Indonesia TVRI Regional', 'radio': 'Radio',
}
baru = []
for l in blok:
    k = re.search(r'key:\s*(\w+)', l).group(1)
    l2 = re.sub(r'label:\s*"[^"]*"', 'label: "%s"' % NAMA[k], l)
    baru.append((k, l2))
d = [x for x in baru if x[0] == 'docs'][0]
baru.remove(d)
pos = [x[0] for x in baru].index('movies') + 1
baru.insert(pos, d)
L[i0:i1] = [x[1] for x in baru]
open('rules.yml', 'w', encoding='utf-8').write('\n'.join(L))
R = yaml.safe_load(open('rules.yml', encoding='utf-8'))
for n, f in enumerate(R['folders'], 1):
    print('%2d  %s' % (n, f['label']))
