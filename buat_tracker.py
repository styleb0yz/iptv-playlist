import csv, datetime, os, re
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.formatting.rule import FormulaRule
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter

SRC = 'docs/revive_status_1511.csv'
OUT = 'docs/tracker_revive.xlsx'
rows = list(csv.DictReader(open(SRC, encoding='utf-8-sig')))
n = len(rows)
last = n + 1
F = 'Arial'
fn = Font(name=F, size=10)
fb = Font(name=F, size=10, bold=True)
fh = Font(name=F, size=10, bold=True, color='FFFFFF')
fin = Font(name=F, size=10, color='0000FF')
ft = Font(name=F, size=14, bold=True)
hdr = PatternFill('solid', fgColor='1F3864')
sec = PatternFill('solid', fgColor='D9E1F2')
inp = PatternFill('solid', fgColor='FFF2CC')
thin = Side(style='thin', color='BFBFBF')
box = Border(left=thin, right=thin, top=thin, bottom=thin)

DRM = {'Cartoon Network (United States)', 'Discovery Channel (India) HD (1080p)', 'Discovery Channel (United Kingdom)', 'Discovery Channel (United States)', 'HBO (United States)', 'HBO Hits', 'HGTV (United States)', 'Mythbusters', 'Nick Jr. (India) (576p)', 'Nickelodeon (India) (576p)', 'Nickelodeon (United Kingdom)', 'PBS Nature'}
RENDAH = ['geo-blocked', 'sky sport', 'espn', 'dazn', 'nfl', 'tnt', 'hbo', 'starz', 'bbc', 'itv', 'channel 4', 'channel 5', 'nbc', 'fox', 'cnbc', 'usa network', 'amc', 'tbs', 'tcm', 'univision', 'premier sports', 'setanta', 'eurosport', 'canale 5', 'polsat', 'sport tv', 'nat geo', 'national geographic', 'discovery', 'cartoon network', 'disney', 'mtv', 'lifetime', 'fx ', 'hallmark', 'bravo', 'abc ', 'cbs', 'trt', 'zdf', 'npo', 'svt', 'france', 'arte', 'dr1', 'e4', 'more4', 'e!', 'comedy central', 'axn', 'sony', 'investigation', 'animal planet', 'pbs']
SEDANG = ['baywatch', "hell's kitchen", 'laff', 'dust', 'mst3k', 'cinevault', 'reelz', 'fight network', 'overtime', 'racer', 'curiosity', 'dancetv', 'k-pop', 'vevo', 'trace', 'hgtv', 'history', 'celestial', 'great!', 'mythbusters', 'golf', 'willow', 'one golf', 'f1', 'barca', 'jimjam', 'babytv', 'cbbc', 'cbeebies', 'nick', 'rt ', 'islam channel', 'al jazeera', 'tve', 'la 2', 'antena 3', 'la sexta', 's4c']

def peluang(r):
    nm = r['nama'].lower() + ' '
    if r['kelompok'] == 'radio_non_hidup':
        return 'Tinggi'
    if r['kelompok'] == 'utama_non_hidup' and any(k in nm for k in ['tv', 'rcti', 'antv', 'mnc', 'trans', 'surau', 'ajwa', 'mentari', 'kidz', 'kids']) and not any(k in nm for k in ['antena', 'la sexta', 's4c', 'hgtv', 'fox', 'beinsports', 'bein']):
        return 'Tinggi'
    if 'indonesia' in nm or 'biznet' in nm or 'my kidz' in nm or 'sctv' in nm:
        return 'Tinggi'
    if any(k in nm for k in RENDAH):
        return 'Rendah'
    if any(k in nm for k in SEDANG):
        return 'Sedang'
    return 'Sedang'

def lokasi(f):
    if f.startswith('Archive · Likely Dead'):
        return 'Archive · Likely Dead'
    if f.startswith('Archive'):
        return f
    if f.startswith('tidak ada'):
        return 'Tidak ada di playlist'
    return 'Folder utama 01-15'

def langkah(r):
    st, nm = r['status_baru'], r['nama']
    if st == 'AMAN_LOLOS_LOKAL':
        return 'Selesai (lolos tes lokal). Cek putar di STB bila sempat.'
    if st == 'AMAN_BELUM_DITES':
        return 'Jalankan bash tes_lokal.sh untuk URL ini.'
    if st == 'TUNGGU_STB':
        return 'Tes putar di TiviMate/STB (DRM/MPD).'
    if st == 'KEPUTUSAN_LATAM':
        return 'Keputusan user: buang atau pertahankan (audio Spanyol).'
    if nm in DRM:
        return 'Kandidat DRM ada di sumber app: tes di STB.'
    if 'geo-blocked' in nm.lower():
        return 'Butuh VPN/proxy negara asal, atau MATI_PERMANEN.'
    if r['kelompok'] == 'radio_non_hidup':
        return 'Cari URL stream pengganti (radio-browser/situs stasiun).'
    if st == 'BELUM_SLOT_ADA_URL_MATI':
        return 'Slot di folder utama, URL mati: cari URL pengganti (web, situs resmi).'
    return 'Cari link web; bila berbayar atau tidak ada sumber gratis: MATI_PERMANEN + alasan.'

wb = Workbook()
ws = wb.active
ws.title = 'Ringkasan'
tk = wb.create_sheet('Tracker')
sc = wb.create_sheet('Sumber & Catatan')

cols = ['No', 'Kelompok', 'Channel', 'Lokasi sekarang', 'Folder sekarang', 'Folder tujuan (TiviMate)', 'Status otomatis', 'Aman?', 'Peluang (DUGAAN)', 'Langkah berikutnya', 'Status akhir (isi)', 'Catatan / alasan (isi)', 'Sumber sudah dicoba']
for j, c in enumerate(cols, 1):
    x = tk.cell(row=1, column=j, value=c)
    x.font, x.fill, x.border = fh, hdr, box
    x.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
for i, r in enumerate(rows, 2):
    st = r['status_baru']
    akhir = 'HIDUP' if st.startswith('AMAN') else ('TUNGGU_STB' if (st == 'TUNGGU_STB' or r['nama'] in DRM) else '')
    cat = ''
    if st == 'AMAN_BELUM_DITES':
        cat = 'URL belum dites lokal.'
    elif r['nama'] in DRM and st != 'TUNGGU_STB':
        cat = 'URL DRM ada di aktv/gvision, butuh STB.'
    sumber = '' if (st.startswith('AMAN') or st in ('TUNGGU_STB', 'KEPUTUSAN_LATAM')) else 'aktv + gvision (cocok nama, 16 Nov)'
    vals = [int(r['no']), r['kelompok'], r['nama'], lokasi(r['folder_sekarang']), r['folder_sekarang'], r['folder_tujuan'], st, '=IF(LEFT(G%d,4)="AMAN","ya","belum")' % i, peluang(r) if not st.startswith('AMAN') else '', langkah(r), akhir, cat, sumber]
    for j, v in enumerate(vals, 1):
        x = tk.cell(row=i, column=j, value=v)
        x.font = fn
        x.border = box
        x.alignment = Alignment(vertical='top', wrap_text=(j in (10, 12, 13)))
    for j in (11, 12):
        tk.cell(row=i, column=j).fill = inp
        tk.cell(row=i, column=j).font = fin
widths = [5, 18, 34, 22, 26, 26, 24, 8, 13, 48, 16, 34, 30]
for j, w in enumerate(widths, 1):
    tk.column_dimensions[get_column_letter(j)].width = w
tk.freeze_panes = 'D2'
tk.auto_filter.ref = 'A1:%s%d' % (get_column_letter(len(cols)), last)
tk.row_dimensions[1].height = 32
dv = DataValidation(type='list', formula1='"HIDUP,TUNGGU_STB,MATI_PERMANEN,CARI_LINK"', allow_blank=True)
tk.add_data_validation(dv)
dv.add('K2:K%d' % last)
rng = 'G2:H%d' % last
tk.conditional_formatting.add(rng, FormulaRule(formula=['LEFT($G2,4)="AMAN"'], fill=PatternFill('solid', bgColor='C6EFCE')))
tk.conditional_formatting.add(rng, FormulaRule(formula=['$G2="TUNGGU_STB"'], fill=PatternFill('solid', bgColor='FFEB9C')))
tk.conditional_formatting.add(rng, FormulaRule(formula=['$G2="KEPUTUSAN_LATAM"'], fill=PatternFill('solid', bgColor='D9D9D9')))
tk.conditional_formatting.add(rng, FormulaRule(formula=['LEFT($G2,5)="BELUM"'], fill=PatternFill('solid', bgColor='FFC7CE')))

def R(c):
    return 'Tracker!$%s$2:$%s$%d' % (c, c, last)
NL = '"<>latam_audio_spanyol"'
ws.sheet_view.showGridLines = False
ws['A1'] = 'Tracker Revive IPTV: channel bermasalah'
ws['A1'].font = ft
ws['A2'] = 'Dibuat %s dari docs/revive_status_1511.csv (hasil revive_status.py). Latam (15) di luar penyebut 253. Tab Tracker bisa difilter; kolom kuning diisi manual.' % datetime.datetime.now().strftime('%d %b %Y %H:%M')
ws['A2'].font = fn

def head(row, labels):
    for j, l in enumerate(labels, 1):
        x = ws.cell(row=row, column=j, value=l)
        x.font, x.fill, x.border = fh, hdr, box
        x.alignment = Alignment(horizontal='center', wrap_text=True)
def put(row, col, v, bold=False, fmt=None, blue=False):
    x = ws.cell(row=row, column=col, value=v)
    x.font = fin if blue else (fb if bold else fn)
    x.border = box
    if fmt:
        x.number_format = fmt
    if blue:
        x.fill = inp
    return x

head(4, ['Progres', 'Nilai'])
lab = ['Penyebut (253 bermasalah, tanpa latam)', 'Aman (ada URL hidup di folder utama)', 'Persen aman', 'Target persen (input)', 'Target jumlah', 'Kurang menuju target']
put(5, 1, lab[0]); put(5, 2, '=COUNTIFS(%s,%s)' % (R('B'), NL))
put(6, 1, lab[1]); put(6, 2, '=COUNTIFS(%s,%s,%s,"ya")' % (R('B'), NL, R('H')))
put(7, 1, lab[2]); put(7, 2, '=IF(B5=0,0,B6/B5)', fmt='0.0%')
put(8, 1, lab[3]); put(8, 2, 0.9, fmt='0%', blue=True)
put(9, 1, lab[4]); put(9, 2, '=ROUNDUP(B5*B8,0)')
put(10, 1, lab[5]); put(10, 2, '=MAX(0,B9-B6)')

r0 = 12
head(r0, ['Per kelompok', 'Total', 'Aman', 'Belum', '% aman'])
for k, kel in enumerate(['likely_dead', 'utama_non_hidup', 'radio_non_hidup']):
    rr = r0 + 1 + k
    put(rr, 1, kel)
    put(rr, 2, '=COUNTIFS(%s,A%d)' % (R('B'), rr))
    put(rr, 3, '=COUNTIFS(%s,A%d,%s,"ya")' % (R('B'), rr, R('H')))
    put(rr, 4, '=B%d-C%d' % (rr, rr))
    put(rr, 5, '=IF(B%d=0,0,C%d/B%d)' % (rr, rr, rr), fmt='0.0%')
rr = r0 + 4
put(rr, 1, 'Total', True)
for c, L in ((2, 'B'), (3, 'C'), (4, 'D')):
    put(rr, c, '=SUM(%s%d:%s%d)' % (L, r0 + 1, L, r0 + 3), True)
put(rr, 5, '=IF(B%d=0,0,C%d/B%d)' % (rr, rr, rr), True, '0.0%')

locs = ['Folder utama 01-15', 'Archive · Likely Dead']
extra = sorted({lokasi(r['folder_sekarang']) for r in rows if r['kelompok'] != 'latam_audio_spanyol'} - set(locs))
locs += extra
r1 = rr + 2
head(r1, ['Per lokasi sekarang (di playlist)', 'Total', 'Aman', 'Belum'])
for k, l in enumerate(locs):
    q = r1 + 1 + k
    put(q, 1, l)
    put(q, 2, '=COUNTIFS(%s,A%d,%s,%s)' % (R('D'), q, R('B'), NL))
    put(q, 3, '=COUNTIFS(%s,A%d,%s,%s,%s,"ya")' % (R('D'), q, R('B'), NL, R('H')))
    put(q, 4, '=B%d-C%d' % (q, q))
r2 = r1 + len(locs) + 2
sts = sorted({r['status_baru'] for r in rows})
head(r2, ['Per status otomatis', 'Jumlah'])
for k, s in enumerate(sts):
    put(r2 + 1 + k, 1, s)
    put(r2 + 1 + k, 2, '=COUNTIFS(%s,A%d)' % (R('G'), r2 + 1 + k))
r3 = r2 + len(sts) + 2
fol = sorted({r['folder_tujuan'] for r in rows if r['kelompok'] != 'latam_audio_spanyol' and r['folder_tujuan']})
head(r3, ['Per folder tujuan (TiviMate)', 'Total', 'Aman', 'Belum'])
for k, f in enumerate(fol):
    q = r3 + 1 + k
    put(q, 1, f)
    put(q, 2, '=COUNTIFS(%s,A%d,%s,%s)' % (R('F'), q, R('B'), NL))
    put(q, 3, '=COUNTIFS(%s,A%d,%s,%s,%s,"ya")' % (R('F'), q, R('B'), NL, R('H')))
    put(q, 4, '=B%d-C%d' % (q, q))
r4 = r3 + len(fol) + 2
head(r4, ['Status akhir (kolom K, tanpa latam)', 'Jumlah'])
for k, s in enumerate(['HIDUP', 'TUNGGU_STB', 'MATI_PERMANEN', 'CARI_LINK']):
    put(r4 + 1 + k, 1, s)
    put(r4 + 1 + k, 2, '=COUNTIFS(%s,A%d,%s,%s)' % (R('K'), r4 + 1 + k, R('B'), NL))
put(r4 + 5, 1, 'Belum diputuskan')
put(r4 + 5, 2, '=COUNTIFS(%s,"",%s,%s)' % (R('K'), R('B'), NL))
put(r4 + 6, 1, 'Selesai = HIDUP + TUNGGU_STB + MATI_PERMANEN', True)
put(r4 + 6, 2, '=SUM(B%d:B%d)' % (r4 + 1, r4 + 3), True)
ws.column_dimensions['A'].width = 44
for c in 'BCDE':
    ws.column_dimensions[c].width = 14

notes = [
    ('Kolom Tracker', ''),
    ('Lokasi sekarang', 'Dari kolom folder_sekarang: folder utama 01-15, Archive Likely Dead, atau archive lain (negara, lokal, internasional).'),
    ('Status otomatis', 'Dari revive_status.py. AMAN_* = ada URL hidup di folder utama. Aman? dihitung dari status ini.'),
    ('Peluang (DUGAAN)', 'Tebakan kasar dari nama channel: Tinggi (Indonesia, radio), Sedang (FAST/sumber gratis mungkin), Rendah (berbayar atau geo-blok). Bukan hasil tes.'),
    ('Status akhir (isi)', 'Dropdown: HIDUP, TUNGGU_STB, MATI_PERMANEN, CARI_LINK. Terisi awal: HIDUP untuk yang aman, TUNGGU_STB untuk yang menunggu STB atau kandidat DRM. Selebihnya kosong sampai diputuskan.'),
    ('Catatan / alasan (isi)', 'Wajib diisi untuk MATI_PERMANEN (alasan: berbayar, geo-blok, tidak ada sumber, dan seterusnya).'),
    ('Sumber sudah dicoba', 'aktv + gvision: pencocokan nama ke semua entri, termasuk URL dikomentari (16 Nov). Hasil: 22 dari 189 channel punya kandidat, 0 aman baru, 12 DRM butuh STB.'),
    ('', ''),
    ('Aturan', ''),
    ('Warna', 'Hijau = aman, kuning = TUNGGU_STB, merah = belum, abu = latam. Sel kuning dengan huruf biru = input manual.'),
    ('Data', 'Tidak ada URL di file ini. URL sumber app tetap di ~/iptv_stb_privat dan tidak boleh masuk GitHub publik.'),
    ('Angka', 'Target persen (0,9) di Ringkasan!B8 adalah input dari user (target 90 persen dari 253 = 228). Ubah di sana kalau target berubah.'),
]
for i, (a, b) in enumerate(notes, 1):
    x = sc.cell(row=i, column=1, value=a)
    y = sc.cell(row=i, column=2, value=b)
    x.font = fb
    y.font = fn
    y.alignment = Alignment(wrap_text=True, vertical='top')
sc.column_dimensions['A'].width = 26
sc.column_dimensions['B'].width = 110
wb.save(OUT)
print('tracker OK:', OUT, '|', n, 'baris')
