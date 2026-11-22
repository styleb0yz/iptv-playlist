import csv, json, re, datetime, collections, yaml
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

rules = yaml.safe_load(open('rules.yml', encoding='utf-8'))
M = yaml.safe_load(open('major_brands.yml', encoding='utf-8'))
FOLDERS = rules['folders']
lab = {f['label']: f for f in FOLDERS}
key2f = {f['key']: f for f in FOLDERS}
num = lambda f: f['csv'].split(' ')[0]
st = json.load(open('data/status_lokal.json', encoding='utf-8'))

def key(s):
    return re.sub(r'[^a-z0-9]+', '', re.sub(r'\[[^\]]*\]|\([^)]*\)', ' ', s.lower()))

def nrm(s):
    s = re.sub(r'\[[^\]]*\]|\([^)]*\)', ' ', s.lower()).replace('&', ' and ').replace('+', ' plus ')
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()

TAGS = {'[MATI]': 'MATI PERMANEN', '[VPN]': 'BUTUH VPN', '[STB]': 'TUNGGU STB', '[BELUM]': 'BELUM FINAL'}

def parse(path):
    out, a, nm = [], {}, ''
    for l in open(path, encoding='utf-8', errors='replace'):
        l = l.strip()
        if l.startswith('#EXTINF'):
            a = dict(re.findall(r'([\w-]+)="([^"]*)"', l))
            nm = l.split(',', 1)[1].strip() if ',' in l else ''
        elif l.startswith('http') and nm:
            out.append(dict(name=nm, tvg=a.get('tvg-id', ''), grup=a.get('group-title', ''), url=l))
            nm = ''
    return out

def info(e):
    m = re.search(r'\s(\[(?:MATI|VPN|STB|BELUM)\])\s*$', e['name'])
    e['tag'] = m.group(1) if m else ''
    s = st.get(e['url'])
    e['tes'] = 'LOLOS' if (s and s.get('ok')) else 'GAGAL' if (s and s.get('ok') is False) else 'BELUM DITES'
    e['tinggi'] = (s or {}).get('height', 0) or 0
    if s and s.get('ok') and s.get('drm'):
        e['tes'] = 'LOLOS (DRM)'
    if e['tag']:
        e['status'] = TAGS[e['tag']]
    elif e['tes'].startswith('LOLOS'):
        e['status'] = 'HIDUP'
    elif e['tes'] == 'GAGAL':
        e['status'] = 'GAGAL TES'
    else:
        e['status'] = 'BELUM DITES'
    m2 = re.search(r'\.([a-z]{2,3})(@|$)', e['tvg'])
    e['cc'] = m2.group(1) if m2 else ''
    return e

ents = [info(e) for e in parse('out/playlist.m3u')]
main = [e for e in ents if e['grup'] in lab]
arch = [e for e in ents if e['grup'] not in lab]
main.sort(key=lambda e: num(lab[e['grup']]))

FILL = {'HIDUP': 'E2EFDA', 'MATI PERMANEN': 'F8CBAD', 'BUTUH VPN': 'DDEBF7', 'TUNGGU STB': 'FFF2CC',
        'BELUM FINAL': 'FCE4D6', 'GAGAL TES': 'EDEDED', 'BELUM DITES': 'EDEDED'}
F = lambda **k: Font(**{'name': 'Arial', 'size': 10, **k})
HDR = PatternFill('solid', fgColor='1F3864')
thin = Side(style='thin', color='BFBFBF')
BOR = Border(left=thin, right=thin, top=thin, bottom=thin)

def tabel(ws, head, rows, widths, status_col=None, start=1):
    for j, h in enumerate(head, 1):
        c = ws.cell(row=start, column=j, value=h)
        c.font = F(bold=True, color='FFFFFF'); c.fill = HDR; c.border = BOR
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    for i, r in enumerate(rows, start + 1):
        for j, v in enumerate(r, 1):
            c = ws.cell(row=i, column=j, value=v)
            c.font = F(); c.border = BOR; c.alignment = Alignment(vertical='top')
        if status_col:
            sv = r[status_col - 1]
            if sv in FILL:
                ws.cell(row=i, column=status_col).fill = PatternFill('solid', fgColor=FILL[sv])
    for j, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = ws.cell(row=start + 1, column=1)
    ws.auto_filter.ref = '%s%d:%s%d' % ('A', start, get_column_letter(len(head)), start + len(rows))
    ws.row_dimensions[start].height = 30

wb = Workbook()
ws0 = wb.active; ws0.title = 'Ringkasan'
ws1 = wb.create_sheet('Folder Utama')
ws2 = wb.create_sheet('Seharusnya Major')
ws3 = wb.create_sheet('Bermasalah Belum Masuk')

rows1, cnt = [], collections.Counter()
for e in main:
    f = lab[e['grup']]
    cnt[f['csv']] += 1
    rows1.append([f['csv'], cnt[f['csv']], re.sub(r'\s\[(?:MATI|VPN|STB|BELUM)\]\s*$', '', e['name']), e['tag'], e['status'], e['tes'], e['tinggi'] or None, e['tvg'], e['cc'].upper()])
tabel(ws1, ['Folder', 'No', 'Nama channel', 'Tanda di playlist', 'Status', 'Tes lokal (Indonesia)', 'Tinggi (p)', 'tvg-id', 'Negara'],
      rows1, [32, 6, 46, 12, 18, 20, 10, 30, 9], status_col=5)

SUF = set(M['suffix_words'])
reg_cc = M['region_cc']
cc2reg = {c: r for r, cs in reg_cc.items() for c in cs}
order = {r: i for i, r in enumerate(M['region_order'])}

def cocok(name, aliases, x=None):
    s = nrm(name)
    if x and re.search(x, name, re.I):
        return False
    for a in aliases:
        a = nrm(a)
        if s == a or (s.startswith(a + ' ') and all(t in SUF for t in s[len(a):].split())):
            return True
    return False

rows2 = []
for i, b in enumerate(M['brands'], 1):
    al = b['a']
    x = b.get('x')
    mm = [e for e in main if cocok(e['name'], al, x)]
    hidup = [e for e in mm if e['status'] == 'HIDUP']
    cand = [e for e in arch if cocok(e['name'], al, x) and e['status'] == 'HIDUP']
    cand.sort(key=lambda e: (order.get(cc2reg.get(e['cc'], 'other'), 9), -e['tinggi']))
    fl = key2f[b['f']]['csv'] if b['f'] in key2f else b['f']
    if hidup:
        di = 'YA, hidup'
    elif mm:
        di = 'YA, tidak hidup'
    else:
        di = 'TIDAK'
    nama_main = '; '.join(sorted({re.sub(r'\s\[(?:MATI|VPN|STB|BELUM)\]\s*$', '', e['name']) for e in mm}))[:120]
    stat_main = '; '.join(sorted({e['status'] for e in mm}))
    if di == 'YA, hidup':
        s_nm = s_grp = s_tvg = ''; s_h = None; saran = '-'
    elif cand:
        c = cand[0]
        saran = 'NAIKKAN dari Archive'
        s_nm, s_grp, s_tvg, s_h = c['name'], c['grup'], c['tvg'], c['tinggi'] or None
    else:
        saran = 'Tidak ada kandidat hidup di sumber lokal'
        s_nm = s_grp = s_tvg = ''; s_h = None
    rows2.append([i, b['n'], fl, di, nama_main, stat_main, saran, s_nm, s_grp, s_h, s_tvg])
tabel(ws2, ['No', 'Merek (daftar major_brands.yml)', 'Folder tujuan', 'Di folder utama?', 'Nama di folder utama', 'Status di folder utama',
            'Saran', 'Kandidat hidup (Archive)', 'Asal grup Archive', 'Tinggi (p)', 'tvg-id kandidat'],
      rows2, [5, 30, 30, 18, 40, 22, 34, 44, 24, 10, 30])
for i, r in enumerate(rows2, 2):
    col = {'YA, hidup': 'E2EFDA', 'YA, tidak hidup': 'FFF2CC', 'TIDAK': 'F8CBAD'}[r[3]]
    ws2.cell(row=i, column=4).fill = PatternFill('solid', fgColor=col)
    if r[6].startswith('NAIKKAN'):
        ws2.cell(row=i, column=7).fill = PatternFill('solid', fgColor='DDEBF7')

mainkeys = {key(e['name']) for e in main}
rows3 = []
for r in csv.DictReader(open('docs/revive_status_1511.csv', encoding='utf-8-sig')):
    if r['status_baru'].startswith('AMAN') or key(r['nama']) in mainkeys:
        continue
    rows3.append([r['nama'], r['kelompok'], r['folder_tujuan'], r['status_baru'], r['keterangan'][:120]])
tabel(ws3, ['Nama channel', 'Kelompok', 'Folder tujuan', 'Status revive', 'Keterangan'], rows3, [46, 20, 28, 28, 70])

ws0['A1'] = 'Channel di folder utama (01-15)'; ws0['A1'].font = F(bold=True, size=14)
ws0['A2'] = 'Dibuat: %s dari out/playlist.m3u, data/status_lokal.json, major_brands.yml, docs/revive_status_1511.csv' % datetime.date.today().isoformat()
ws0['A2'].font = F(italic=True, color='595959')
head = ['Folder', 'Total', 'HIDUP', 'BUTUH VPN', 'TUNGGU STB', 'MATI PERMANEN', 'BELUM FINAL', 'GAGAL TES / BELUM DITES']
for j, h in enumerate(head, 1):
    c = ws0.cell(row=4, column=j, value=h)
    c.font = F(bold=True, color='FFFFFF'); c.fill = HDR; c.border = BOR
    c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
ws0.row_dimensions[4].height = 30
fo = sorted(FOLDERS, key=num)
r0 = 5
for i, f in enumerate(fo):
    r = r0 + i
    ws0.cell(row=r, column=1, value=f['csv'])
    ws0.cell(row=r, column=2, value="=COUNTIF('Folder Utama'!$A:$A,A%d)" % r)
    for j, s in enumerate(['HIDUP', 'BUTUH VPN', 'TUNGGU STB', 'MATI PERMANEN', 'BELUM FINAL'], 3):
        ws0.cell(row=r, column=j, value="=COUNTIFS('Folder Utama'!$A:$A,$A%d,'Folder Utama'!$E:$E,\"%s\")" % (r, s))
    ws0.cell(row=r, column=8, value='=B%d-SUM(C%d:G%d)' % (r, r, r))
rl = r0 + len(fo)
ws0.cell(row=rl, column=1, value='TOTAL')
for j in range(2, 9):
    L = get_column_letter(j)
    ws0.cell(row=rl, column=j, value='=SUM(%s%d:%s%d)' % (L, r0, L, rl - 1))
for r in range(r0, rl + 1):
    for j in range(1, 9):
        c = ws0.cell(row=r, column=j); c.font = F(bold=(r == rl)); c.border = BOR
        if j > 1:
            c.alignment = Alignment(horizontal='center')
r2 = rl + 2
ws0.cell(row=r2, column=1, value='Merek major (major_brands.yml)').font = F(bold=True, size=12)
for k, (t, v) in enumerate([('Sudah ada di folder utama dan hidup', 'YA, hidup'), ('Ada di folder utama tapi tidak hidup', 'YA, tidak hidup'), ('Belum ada di folder utama', 'TIDAK')], 1):
    ws0.cell(row=r2 + k, column=1, value=t).font = F()
    c = ws0.cell(row=r2 + k, column=2, value="=COUNTIF('Seharusnya Major'!$D:$D,\"%s\")" % v); c.font = F()
ws0.cell(row=r2 + 4, column=1, value='Punya kandidat hidup di Archive (NAIKKAN)').font = F()
ws0.cell(row=r2 + 4, column=2, value="=COUNTIF('Seharusnya Major'!$G:$G,\"NAIKKAN*\")").font = F()
ws0.cell(row=r2 + 6, column=1, value='Channel bermasalah yang belum masuk folder utama').font = F()
ws0.cell(row=r2 + 6, column=2, value="=COUNTA('Bermasalah Belum Masuk'!$A:$A)-1").font = F()
n0 = r2 + 8
ws0.cell(row=n0, column=1, value='Keterangan').font = F(bold=True)
for k, t in enumerate([
    'Status HIDUP = lolos tes lokal dari Indonesia tanpa tanda. Tanda [MATI], [VPN], [STB], [BELUM] ada di nama playlist.',
    'Daftar "Seharusnya Major" memakai major_brands.yml (176 merek); pencocokan nama tanpa memeriksa wilayah, jadi cek negara kandidat sebelum menaikkan.',
    'Lolos tes lokal belum membuktikan identitas channel (lihat frame). Angka di tabel ini rumus, hitung ulang saat file dibuka.'], 1):
    ws0.cell(row=n0 + k, column=1, value=t).font = F()
ws0.column_dimensions['A'].width = 46
for L in 'BCDEFGH':
    ws0.column_dimensions[L].width = 16
wb.save('docs/channel_major.xlsx')
print('folder utama:', len(rows1), 'channel | merek major:', len(rows2), '| bermasalah belum masuk:', len(rows3), '| arsip dibaca:', len(arch))
print('simpan: docs/channel_major.xlsx')
