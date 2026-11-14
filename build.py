#!/usr/bin/env python3
"""Gabung index.m3u (iptv-org) + dhanytv.m3u jadi satu playlist TiviMate + laporan.md.
Pakai: python build.py --index index.m3u --dhany dhanytv.m3u --draft draft_esensial.csv --out out
"""
import argparse, collections, csv, datetime, json, re, sys, unicodedata
from pathlib import Path
import yaml

OPT = re.compile(r'#(EXTVLCOPT|EXTHTTP|KODIPROP)\b')
ATTR = re.compile(r'\s*([\w-]+)="([^"]*)"')


# ---------------------------------------------------------------- parsing
def parse_extinf(line):
    m = re.match(r'#EXTINF:\s*(-?[\d.]+)\s*', line)
    rest, pos, attrs = line[m.end():], 0, {}
    while True:
        a = ATTR.match(rest, pos)
        if not a:
            break
        attrs[a.group(1)] = a.group(2)
        pos = a.end()
    return attrs, rest[pos:].strip().lstrip(',').strip()


def parse_m3u(path, src):
    """Baris opsi sebelum #EXTINF (setelah URL entri lalu) -> entri berikutnya;
    opsi di antara #EXTINF dan URL -> entri itu. URL tanpa #EXTINF aktif (entri
    yang di-comment) diabaikan dan membuang opsi yatim di depannya."""
    ents, pending, cur, bad = [], [], None, 0
    for raw in Path(path).read_text(encoding='utf-8-sig', errors='replace').splitlines():
        l = raw.strip()
        if not l:
            continue
        if l.startswith('#EXTINF'):
            if cur is not None:
                bad += 1
            attrs, name = parse_extinf(l)
            cur = dict(src=src, attrs=attrs, name=name, opts=pending, url=None)
            pending = []
        elif OPT.match(l):
            (cur['opts'] if cur is not None else pending).append(l)
        elif l.startswith('#'):
            continue
        elif cur is not None:
            cur['url'] = l
            ents.append(cur)
            cur = None
        else:
            pending = []  # URL yatim
    if cur is not None:
        bad += 1
    return ents, bad


# ---------------------------------------------------------------- normalisasi
def norm_name(s):
    s = re.sub(r'\(\s*\d+[pi]\s*\)|\[[^\]]*\]', ' ', s)
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\b(hd|fhd|uhd|sd|4k)\b', ' ', s)
    return re.sub(r'[^a-z0-9]', '', s)


CC_GROUP = {}


def enrich(e, qual, order, known_cc):
    tvg = e['attrs'].get('tvg-id', '')
    t = re.sub(r'^auto\.', '', tvg, flags=re.I)
    base, _, suf = t.partition('@')
    base_l = base.lower()
    e.update(tvg=tvg, base=base_l, suf=suf, norm=norm_name(e['name']), order=order)
    cc = base_l.rsplit('.', 1)[-1] if '.' in base_l else ''
    e['country'] = cc if cc in known_cc else ''
    if not e['country'] and e['src'] == 'dhany':
        e['country'] = CC_GROUP.get(e['attrs'].get('group-title', ''), '')
    if e['src'] == 'iptv':
        e['key'] = base_l if (not suf or qual.match(suf)) else f'{base_l}@{suf.lower()}'
    else:
        e['key'] = base_l or 'name:' + e['norm']
    h = re.search(r'\((\d{3,4})[pi]\)', e['name'])
    e['h_label'] = int(h.group(1)) if h else 0
    e['n247'] = '[Not 24/7]' in e['name']
    e['geo'] = '[Geo-blocked]' in e['name']
    e['pluto'] = 'jmp2.uk/plu-' in e['url'] or 'images.pluto.tv' in e['attrs'].get('tvg-logo', '')
    e['drm'] = any('license_type' in o or 'license_key' in o for o in e['opts'])
    e['religi'] = 'religious' in e['attrs'].get('group-title', '').lower().split(';')
    return e


# ---------------------------------------------------------------- status & ranking
class Status:
    def __init__(self, local, github, exempt, min_fails=1):
        self.local, self.github, self.exempt, self.min_fails = local, github, set(exempt), min_fails

    def st(self, e):
        """0 lolos lokal, 1 belum dites, 2 gagal (dianggap mati)."""
        l = self.local.get(e['url'], {}).get('ok')
        if l is not None:          # tes di jaringan user selalu menang atas cek GitHub
            return 0 if l else 2
        g = self.github.get(e['url'], {})
        if g.get('ok') is False and g.get('fails', 1) >= self.min_fails \
                and e['country'] not in self.exempt and not e['geo']:
            return 2
        return 1

    def res(self, e):
        h = self.local.get(e['url'], {}).get('height') or 0
        return h or e['h_label']

    def rank(self, e):
        # tes jalan > (DRM kalah) > resolusi > bukan Not 24/7 > bukan Geo-blocked > iptv-org > urutan
        return (self.st(e), e['drm'], -self.res(e), e['n247'], e['geo'],
                0 if e['src'] == 'iptv' else 1, e['order'])


def load_json(p):
    try:
        return json.loads(Path(p).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}


# ---------------------------------------------------------------- output
def extinf(e, group, name, tvg):
    attrs = {k: v for k, v in e['attrs'].items() if k != 'tvg-id' and not k.endswith('group-title')}
    parts = []
    if tvg:
        parts.append(f'tvg-id="{tvg}"')
    parts += [f'{k}="{v}"' for k, v in attrs.items()]
    parts.append(f'group-title="{group}"')
    return f'#EXTINF:-1 {" ".join(parts)},{name}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--index', default='index.m3u')
    ap.add_argument('--dhany', default='dhanytv.m3u')
    ap.add_argument('--draft', default='draft_esensial.csv')
    ap.add_argument('--rules', default=str(Path(__file__).with_name('rules.yml')))
    ap.add_argument('--dir', default='.', help='lokasi status_*.json, radio_cache.json, epg_ids.txt')
    ap.add_argument('--out', default='out')
    ap.add_argument('--require-radio', action='store_true', help='gagal kalau stasiun radio ID nol (CI)')
    a = ap.parse_args()

    R = yaml.safe_load(Path(a.rules).read_text(encoding='utf-8'))
    D, out = Path(a.dir), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    qual = re.compile(R['quality_suffix'], re.I)
    CC_GROUP.update(R.get('country_from_dhany_group', {}))
    known_cc = set(R['countries']) | {'id'} | {c for v in R['regions'].values() for c in v}
    S = Status(load_json(D / R['files']['status_lokal']), load_json(D / R['files']['status_github']),
               R['dead_exempt_countries'], R.get('github_dead_after_fails', 1))

    # --- baca sumber
    iptv, bad1 = parse_m3u(a.index, 'iptv')
    dh, bad2 = parse_m3u(a.dhany, 'dhany')
    # sumber tambahan: semua data/extra/*.m3u diperlakukan seperti dhanytv (urutan kalah dari iptv-org kalau seri).
    # Pasang tvg-id yang SAMA dengan id iptv-org supaya entrinya bergabung ke channel itu (lihat README.md).
    n_extra = 0
    xdir = D / 'extra'
    for xf in (sorted(xdir.glob('*.m3u')) if xdir.is_dir() else []):
        xe, _ = parse_m3u(xf, 'dhany')
        for e in xe:
            e['origin'] = 'extra:' + xf.name
        dh += xe
        n_extra += len(xe)
        print(f'  sumber tambahan {xf.name}: {len(xe)} entri')
    for i, e in enumerate(iptv):
        enrich(e, qual, i, known_cc)
    for i, e in enumerate(dh):
        enrich(e, qual, 100000 + i, known_cc)

    # --- radio (cache Radio Browser)
    radio = []
    for i, r in enumerate(load_json(D / R['files']['radio_cache']) or []):
        if r.get('url'):
            e = dict(src='radio', attrs={'tvg-logo': r.get('logo', '')} if r.get('logo') else {},
                     name=r['name'], opts=[], url=r['url'])
            enrich(e, qual, 200000 + i, known_cc)
            radio.append(e)
    n_radio_id = len(radio)
    if a.require_radio and n_radio_id == 0:
        sys.exit('GAGAL: stasiun radio Indonesia nol (cache kosong).')

    # --- grup (satu channel = satu grup)
    groups = collections.OrderedDict()
    for e in iptv:
        groups.setdefault(e['key'], []).append(e)
    by_base = collections.defaultdict(list)
    for k in groups:
        by_base[k.split('@')[0]].append(k)
    by_name, dh_names = {}, {}
    for k, ms in groups.items():
        for m in ms:
            if m['country']:
                by_name.setdefault((m['norm'], m['country']), k)
    for e in dh:
        k = e['key']
        if k not in groups:
            k2 = by_name.get((e['norm'], e['country'])) if e['country'] else None
            k2 = k2 or next((c for c in by_base.get(e['base'], []) if any(m['norm'] == e['norm'] for m in groups[c])), None)
            if not k2 and len(e['norm']) >= 4:  # sesama dhanytv-murni: nama sama, negara sama atau salah satunya kosong
                k2 = next((kk for (nn, cc), kk in dh_names.items()
                           if nn == e['norm'] and (cc == e['country'] or not cc or not e['country'])), None)
            k = k2 or 'dh:' + k
            dh_names.setdefault((e['norm'], e['country']), k)
        groups.setdefault(k, []).append(e)

    # --- draft: baris -> grup
    draft = list(csv.DictReader(open(a.draft, encoding='utf-8-sig', newline='')))
    entry_by_tvg = {}
    for e in iptv:
        entry_by_tvg.setdefault(e['tvg'].lower(), e)
    g_of = {id(e): k for k, ms in groups.items() for e in ms}
    gdraft, draft_missing, draft_dupe = {}, [], []
    for i, row in enumerate(draft):
        e = entry_by_tvg.get(row['tvg_id'].lower())
        if not e:
            draft_missing.append(row)
            continue
        k = g_of[id(e)]
        if k in gdraft:
            draft_dupe.append(row)
            continue
        gdraft[k] = (row['folder'], row['nama'], i)  # folder dipetakan nanti

    # --- penomoran folder (esensial dari rules.folders, lalu archive)
    FL = {f['key']: f"{i:02d} · {f['label']}" for i, f in enumerate(R['folders'], 1)}
    csv2label = {f['csv']: FL[f['key']] for f in R['folders']}
    unmapped = {r['folder'] for r in draft} - set(csv2label)
    assert not unmapped, f'folder draft belum ada di rules.folders: {unmapped}'
    arch = {}
    n = len(R['folders']) + 1
    for it in R['archive']:
        arch[it['key']] = f"{n:02d} · Archive · {it['label']}"; n += 1
    for cc, nm in R['countries'].items():
        arch['c:' + cc] = f"{n:02d} · Archive · {nm}"; n += 1
    cc_region = {}
    for rg, ccs in R['regions'].items():
        arch['r:' + rg] = f"{n:02d} · Archive · {rg}"; n += 1
        for c in ccs:
            cc_region[c] = rg
    DEAD = f"{n:02d} · Archive · {R['dead_label']}"; n += 1
    OTHER = f"{n:02d} · Archive · {R['other_label']}"

    def route(e):
        if e['pluto']: return arch['pluto']
        if e['country'] == 'id': return arch['local_id']
        if e['religi']: return arch['religi']
        if e['country'] in R['countries']: return arch['c:' + e['country']]
        if e['country'] in cc_region: return arch['r:' + cc_region[e['country']]]
        return OTHER

    placed, dupes, held, gap_report = [], [], [], []  # placed: (folder, order, name, entry)
    hold_c = {h['canon']: h['alasan'] for h in R['hold']}

    pin = set(R.get('pin') or [])  # nama channel yang tetap di foldernya walau gagal tes (lihat rules.yml)

    def place(e, folder, name=None, pos=None):
        if S.st(e) == 2 and (name or e['name']) not in pin:
            folder = DEAD
        placed.append((folder, pos if pos is not None else 10**6 + e['order'], name or e['name'], e))

    for k, ms in groups.items():
        ms = sorted(ms, key=S.rank)
        w = ms[0]
        has_iptv = any(m['src'] == 'iptv' for m in ms)
        # ditahan
        if not has_iptv and w['base'] in hold_c:
            for m in ms:
                held.append((m, hold_c[w['base']]))
            continue
        # gap Indonesia (hanya grup dhanytv-murni)
        gap = None if has_iptv else next((g for g in R['gaps'] if
              g.get('canon') == w['base'] or (g.get('name_regex') and re.search(g['name_regex'], w['name'], re.I))), None)
        if gap:
            if S.st(w) == 0 or not R.get('gap_require_local', True):
                place(w, FL[gap['folder']], gap['nama'], 10**5 + w['order'])
                gap_report.append((gap['nama'], 'MASUK', w['url']))
                dupes += [(m, 'varian gap lain') for m in ms[1:]]
            else:
                for m in ms:
                    held.append((m, f"gap {gap['nama']}: belum lolos cek lokal"))
                gap_report.append((gap['nama'], 'DITAHAN (belum lolos cek lokal)', ''))
            continue
        # grup biasa
        if k in gdraft:
            folder, nama, pos = gdraft[k]
            folder = csv2label[folder]
            place(w, folder, nama, pos)
        else:
            place(w, route(w))
        for m in ms[1:]:
            if m['src'] == 'dhany' and R['dhanytv_loser'] == 'report':
                dupes.append((m, 'duplikat ' + w['src'] + ': ' + w['name']))
            else:
                place(m, route(m))

    # --- radio: 8 dari draft sudah di folder 15; stasiun API ditambah di belakang
    seen_url = set()
    for e in radio:
        if e['url'] in seen_url:
            dupes.append((e, 'url radio dobel')); continue
        seen_url.add(e['url'])
        place(e, FL['radio'])

    # --- URL sama dipakai >1 entri = stream yang sama: sisakan satu (folder bernomor terkecil).
    # Entri di folder esensial (01-15, hasil kurasi draft) tidak pernah dibuang; yang dibuang hanya salinan di folder arsip, dicatat di laporan.
    n_ess = len(R['folders'])
    first_u, drop_i = {}, set()
    for i in sorted(range(len(placed)), key=lambda i: (int(placed[i][0][:2]), placed[i][1])):
        f_, _, nm_, e_ = placed[i]
        if e_['url'] not in first_u:
            first_u[e_['url']] = i
        elif int(f_[:2]) > n_ess:
            drop_i.add(i)
            k_ = placed[first_u[e_['url']]]
            dupes.append((e_, f'URL sama dengan "{k_[2]}" (folder {k_[0][:2]})'))
    placed[:] = [p_ for i, p_ in enumerate(placed) if i not in drop_i]
    n_url_dedup = len(drop_i)

    # --- pemeriksaan konsistensi
    total_in = len(iptv) + len(dh) + len(radio)
    total_out = len(placed) + len(dupes) + len(held)
    ids = [id(p[3]) for p in placed]
    assert len(ids) == len(set(ids)), 'ada entri masuk >1 folder'
    assert total_in == total_out, f'total tidak konsisten: masuk {total_in}, keluar {total_out}'

    # --- kandidat untuk check_local.py: semua anggota grup esensial + gap
    def cinfo(m):
        return dict(url=m['url'], name=m['name'], tvg=m['tvg'], src=m['src'], country=m['country'], geo=m['geo'],
                    opts=m['opts'], attrs={x: m['attrs'][x] for x in ('http-user-agent', 'http-referrer') if x in m['attrs']})
    cand, seen_c = [], set()
    for k, ms in groups.items():
        if k in gdraft or any(m['base'] in {g.get('canon') for g in R['gaps']} for m in ms) or \
           any(g.get('name_regex') and re.search(g['name_regex'], m['name'], re.I) for g in R['gaps'] for m in ms if m['src'] == 'dhany'):
            for m in ms:
                if m['url'] not in seen_c:
                    seen_c.add(m['url'])
                    cand.append(cinfo(m))
    (out / 'kandidat_cek.json').write_text(json.dumps(cand, ensure_ascii=False, indent=0), encoding='utf-8')
    allc = {}
    for _, _, _, m in placed:
        allc.setdefault(m['url'], cinfo(m))
    (out / 'kandidat_semua.json').write_text(json.dumps(list(allc.values()), ensure_ascii=False, indent=0), encoding='utf-8')

    # --- EPG (hook)
    epg_ids = set()
    ep = D / R['files']['epg_ids']
    if R['epg']['mode'] == 'single' and ep.exists():
        epg_ids = {x.strip() for x in ep.read_text(encoding='utf-8').splitlines() if x.strip()}
    header = '#EXTM3U' if R['epg']['mode'] == 'off' else f"#EXTM3U url-tvg=\"{R['epg']['url']}\""
    remap_n = 0

    def out_tvg(e):
        nonlocal remap_n
        if not epg_ids:
            return e['tvg']
        cands = [e['tvg'], re.sub(r'^auto\.', '', e['tvg'].split('@')[0], flags=re.I)]
        cands += [m['tvg'] for m in groups[g_of[id(e)]]] if id(e) in g_of else []
        for c in cands:
            if c in epg_ids:
                remap_n += c != e['tvg']
                return c
        return e['tvg']

    placed.sort(key=lambda p: (int(p[0][:2]), p[1], p[2].casefold()))
    lines = [header]
    for folder, _, name, e in placed:
        lines.append(extinf(e, folder, name, out_tvg(e)))
        lines += e['opts']
        lines.append(e['url'])
    (out / 'playlist.m3u').write_text('\n'.join(lines) + '\n', encoding='utf-8')

    # --- channels.json (id kanonik disimpan untuk EPG opsi 3 + diff antar run)
    chans = [dict(key=(e['tvg'] or e['name']) + '|' + e['url'], tvg=e['tvg'], canon=e['base'], name=name,
                  folder=folder, src=e['src'], url=e['url']) for folder, _, name, e in placed]
    prev = {c['key'] for c in load_json(out / 'channels.json') or []} if (out / 'channels.json').exists() else None
    (out / 'channels.json').write_text(json.dumps(chans, ensure_ascii=False, indent=0), encoding='utf-8')
    cur = {c['key'] for c in chans}

    # --- laporan
    per = collections.Counter(p[0] for p in placed)
    from_dh = [(f, nm, e) for f, _, nm, e in placed if e['src'] == 'dhany']
    dead = [(nm, e) for f, _, nm, e in placed if f == DEAD]
    fs = load_json(D / 'fetch_status.json')
    fetch_lines = [f'- {k}: {v.get("status")} ({v.get("entries")} entri) {v.get("reason", "")}' for k, v in fs.items()] \
        or ['- fetch_status.json tidak ada (build manual)']
    L = ['# Laporan build', f'_{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}_', '',
         '## Ringkasan',
         f'- Masuk: iptv-org {len(iptv)}, dhanytv {len(dh)}, radio cache {len(radio)} = **{total_in}**',
         f'- Keluar: playlist {len(placed)} + duplikat dhanytv/radio/URL-sama (hanya dicatat) {len(dupes)} + ditahan {len(held)} = **{total_out}**',
         f'- Entri tanpa URL dilewati: iptv {bad1}, dhanytv {bad2}',
         f'- Kandidat untuk check_local.py: {len(cand)} URL (kandidat_cek.json)',
         f'- Status lokal dimuat: {len(S.local)} URL | status GitHub: {len(S.github)} URL',
         f'- Stasiun radio Indonesia dari cache: {n_radio_id}' + ('  **(NOL, jalankan Batch 3 / workflow)**' if not n_radio_id else ''),
         '', '## Sumber hari ini'] + fetch_lines + ['',
         '## EPG',
         f"- Mode: `{R['epg']['mode']}`. Remap tvg-id: {remap_n} entri. Sumber di rules.yml (epg.sources): {len(R['epg'].get('sources') or [])}.",
         '- Cakupan per folder: `python epg_check.py --epg FILE.xml --playlist out/playlist.m3u --out /tmp/ids.txt`.',
         '', '## Per folder']
    L += [f'- {f}: {c}' for f, c in sorted(per.items(), key=lambda x: int(x[0][:2]))]
    st_lbl = {0: 'LOLOS tes lokal', 1: 'belum dites', 2: 'GAGAL tes lokal'}
    pin_rows = [(f, nm, st_lbl[S.st(e)], e['url']) for f, _, nm, e in placed if nm in pin and int(f[:2]) <= n_ess]
    L += ['', f'## Pin aktif ({len(pin_rows)} dari {len(pin)} nama di rules.yml)']
    L += [f'- {nm} -> {f[:2]}: {stt}  {u[:70]}' for f, nm, stt, u in pin_rows]
    L += ['', f'## Dibuang karena URL sama ({n_url_dedup}, hanya salinan di folder arsip; detail di bagian Duplikat)']
    L += ['', '## Gap Indonesia'] + [f'- {n_}: {s} {u}' for n_, s, u in gap_report]
    L += [f'- MNCTV dkk (ditahan): {sum(1 for m, r in held if m["base"] in hold_c)} entri, {list(hold_c.values())[0]}'
          if hold_c else '']
    L += ['', f'## Berasal dari dhanytv ({len(from_dh)} masuk playlist)']
    L += [f'- {nm} -> {f}' for f, nm, e in from_dh[:80]]
    if len(from_dh) > 80:
        L.append(f'- ... +{len(from_dh) - 80} lagi (lihat channels.json, src=dhany)')
    L += ['', f'## Duplikat yang kalah ({len(dupes)}, hanya dicatat)']
    L += [f'- {m["name"]} ({m["tvg"]}) : {why}' for m, why in dupes[:40]]
    if len(dupes) > 40:
        L.append(f'- ... +{len(dupes) - 40} lagi')
    L += ['', f'## Ditahan ({len(held)})'] + [f'- {m["name"]} ({m["tvg"]}) : {why}' for m, why in held[:40]]
    L += ['', f'## Kemungkinan Mati ({len(dead)})'] + [f'- {nm} ({e["src"]})' for nm, e in dead[:60]]
    L += ['', f'## Draft tidak ketemu di index.m3u ({len(draft_missing)})'] + \
         [f'- {r["nama"]} / {r["tvg_id"]} ({r["folder"]})' for r in draft_missing]
    L += ['', f'## Baris draft dobel dalam satu channel ({len(draft_dupe)})'] + \
         [f'- {r["nama"]} / {r["tvg_id"]}' for r in draft_dupe]
    if prev is None:
        L += ['', '## Diff vs run sebelumnya', '- run pertama, belum ada pembanding']
    else:
        new, gone = sorted(cur - prev), sorted(prev - cur)
        L += ['', f'## Baru ({len(new)})'] + [f'- {k.split("|")[0]}' for k in new[:40]]
        L += ['', f'## Hilang ({len(gone)})'] + [f'- {k.split("|")[0]}' for k in gone[:40]]
    (out / 'laporan.md').write_text('\n'.join(L) + '\n', encoding='utf-8')

    print(f'OK  masuk={total_in}  playlist={len(placed)}  duplikat={len(dupes)}  ditahan={len(held)}')
    print(f'    dari dhanytv={len(from_dh)}  mati={len(dead)}  draft hilang={len(draft_missing)}')
    if n_extra:
        print(f'    (dari dhanytv termasuk {n_extra} entri sumber tambahan)')
    print(f'    dibuang karena URL sama (folder arsip saja)={n_url_dedup}')
    for f, c in sorted(per.items(), key=lambda x: int(x[0][:2])):
        print(f'    {c:5d}  {f}')


if __name__ == '__main__':
    main()
