#!/usr/bin/env python3
"""Isi ulang folder utama dengan merek channel MAYOR yang dicari di SEMUA entri sumber (index.m3u + dhanytv.m3u + data/extra/*.m3u).

  python refill.py scan     # baca semua entri, cocokkan dengan major_brands.yml, tulis out/refill_kandidat.json + out/refill_scan.txt
  (lalu tes stream dari WiFi rumah: check_local.py out/refill_kandidat.json -o data/status_lokal.json ...)
  python refill.py apply    # pilih varian yang LOLOS tes untuk merek yang belum punya channel hidup di folder 01-15,
                            # tulis data/refill_pick.json + out/refill_laporan.txt (build.py membacanya)

Dijalankan lewat refill.sh. Tidak mengubah draft_esensial.csv maupun rules.yml.
Aturan: hanya status LOLOS tes lokal yang dinaikkan. Belum dites atau gagal tidak pernah dinaikkan. Entri DRM dan entri dengan
kredensial di URL (user/password) tidak pernah dipilih.
"""
import argparse, collections, json, re, sys, unicodedata
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

import yaml

sys.path.insert(0, str(Path(__file__).parent))
import build  # parse_m3u, enrich

HERE = Path(__file__).parent


# ---------------------------------------------------------------- normalisasi
def nrm(s):
    s = re.sub(r'\(\s*\d+[pi]\s*\)|\[[^\]]*\]', ' ', s)
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    s = s.replace('&', ' and ').replace('+', ' plus ')
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def nrm_tvg(tvg):
    base = tvg.split('@')[0]
    base = re.sub(r'^auto\.', '', base, flags=re.I)
    base = re.sub(r'(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])', ' ', base)
    return nrm(base.replace('.', ' '))


def texts_for(name, tvg, qual):
    """Teks yang dicocokkan dengan alias: nama channel, plus tvg-id hanya kalau feed-nya polos (tanpa @KXXV, @NorthEast dst)."""
    _, _, suf = tvg.partition('@')
    t = [nrm(name)]
    if not suf or qual.match(suf) or suf.lower() in ('east', 'west'):
        t.append(nrm_tvg(tvg))
    return tuple(t)


def clean_name(name):
    return re.sub(r'\s+', ' ', re.sub(r'\(\s*\d+[pi]\s*\)|\[[^\]]*\]', ' ', name)).strip()


def has_cred(u):
    p = urlsplit(u)
    if p.username or p.password:
        return True
    q = {k.lower() for k in parse_qs(p.query)}
    if 'username' in q or 'password' in q or ('user' in q and 'pass' in q):
        return True
    # pola Xtream: /USER/PASS/ID atau /live/USER/PASS/ID (akun orang di path URL)
    return bool(re.search(r'^/(?:(?:live|movie|series|play)/)?[^/]+/[^/]+/\d+(?:\.\w+)?$', p.path))


# ---------------------------------------------------------------- katalog
class Brand:
    def __init__(self, d, idx, M):
        self.n, self.f, self.idx = d['n'], d['f'], idx
        suf = '|'.join(re.escape(w) for w in M['suffix_words'])
        al = '|'.join(re.escape(nrm(x)).replace('\\ ', ' ') for x in d['a'])
        self.re = re.compile(rf'^(?:{al})(?: (?:{suf}))*$')
        self.x = re.compile(d['x'], re.I) if d.get('x') else None
        AR = M['allowed_regions']
        self.allowed = set(d.get('r') or AR.get(d['f']) or AR['default'])

    def hit(self, texts):
        return any(self.re.search(t) and not (self.x and self.x.search(t)) for t in texts if t)


def region_of(e, M):
    """Petunjuk di nama (Asia, Latin America, UK) menang atas kode negara di tvg-id: HBOSignature.us@LatinAmerica adalah feed Latin America."""
    txt = nrm(e['name'] + ' ' + e['tvg'].partition('@')[2])
    for rg in ('asia', 'latam', 'uk', 'eu'):
        if any(re.search(p, txt) for p in M['region_hints'][rg]):
            return rg
    cc = e['base'].rsplit('.', 1)[-1] if '.' in e['base'] else ''
    cc = cc if re.fullmatch(r'[a-z]{2}', cc) else ''
    if cc:
        for rg, ccs in M['region_cc'].items():
            if cc in ccs:
                return rg
        return 'foreign'
    if any(re.search(p, txt) for p in M['region_hints']['us']):
        return 'us'
    return 'other'


def load_entries(a, R):
    qual = re.compile(R['quality_suffix'], re.I)
    build.CC_GROUP.update(R.get('country_from_dhany_group', {}))
    known_cc = set(R['countries']) | {'id'} | {c for v in R['regions'].values() for c in v}
    iptv, _ = build.parse_m3u(a.index, 'iptv')
    dh, _ = build.parse_m3u(a.dhany, 'dhany')
    xdir = Path(a.dir) / 'extra'
    for xf in (sorted(xdir.glob('*.m3u')) if xdir.is_dir() else []):
        xe, _ = build.parse_m3u(xf, 'dhany')
        dh += xe
    for i, e in enumerate(iptv):
        build.enrich(e, qual, i, known_cc)
    for i, e in enumerate(dh):
        build.enrich(e, qual, 100000 + i, known_cc)
    return iptv, dh


def match_all(ents, brands, M, qual):
    """Satu URL = satu merek (merek yang lebih dulu di katalog menang). Entri di luar wilayah yang diterima merek dibuang (dihitung di skip)."""
    by_brand, seen, skip = collections.defaultdict(list), {}, collections.Counter()
    for e in ents:
        if not e['url'] or not re.match(r'https?://', e['url']):
            continue
        texts = texts_for(e['name'], e['tvg'], qual)
        for b in brands:
            if b.hit(texts):
                if e['url'] not in seen:
                    seen[e['url']] = b.n
                    e['_rg'] = region_of(e, M)
                    if e['_rg'] in b.allowed:
                        by_brand[b.n].append(e)
                    else:
                        skip[b.n] += 1
                break
    return by_brand, skip


def local_ok(S, e):
    return S.local.get(e['url'], {}).get('ok')


def cinfo(m):
    return dict(url=m['url'], name=m['name'], tvg=m['tvg'], src=m['src'], country=m['country'], geo=m['geo'], opts=m['opts'],
                attrs={x: m['attrs'][x] for x in ('http-user-agent', 'http-referrer') if x in m['attrs']})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['scan', 'apply'])
    ap.add_argument('--index', default='data/index.m3u')
    ap.add_argument('--dhany', default='data/dhanytv.m3u')
    ap.add_argument('--dir', default='data')
    ap.add_argument('--out', default='out')
    ap.add_argument('--rules', default=str(HERE / 'rules.yml'))
    ap.add_argument('--brands', default=str(HERE / 'major_brands.yml'))
    ap.add_argument('--per-brand', type=int, default=25, help='maks kandidat dites per merek (urut: wilayah, bukan geo-blocked, resolusi)')
    a = ap.parse_args()

    R = yaml.safe_load(Path(a.rules).read_text(encoding='utf-8'))
    M = yaml.safe_load(Path(a.brands).read_text(encoding='utf-8'))
    brands = [Brand(d, i, M) for i, d in enumerate(M['brands'])]
    out, D = Path(a.out), Path(a.dir)
    out.mkdir(parents=True, exist_ok=True)
    iptv, dh = load_entries(a, R)
    ents = iptv + dh
    qual = re.compile(R['quality_suffix'], re.I)
    by_brand, skip = match_all(ents, brands, M, qual)
    reg_i = {r: i for i, r in enumerate(M['region_order'])}

    S = build.Status(build.load_json(D / R['files']['status_lokal']), {}, [], 1)
    chp = out / 'channels.json'
    chans = build.load_json(chp) if chp.exists() else []
    chans = chans if isinstance(chans, list) else []
    n_ess = len(R['folders'])
    FL = {f['key']: f"{i:02d} · {f['label']}" for i, f in enumerate(R['folders'], 1)}
    pick_old = build.load_json(D / 'refill_pick.json')
    pick_old = {p['url'] for p in pick_old} if isinstance(pick_old, list) else set()
    main_now = [c for c in chans if c['folder'][:2].isdigit() and int(c['folder'][:2]) <= n_ess and c['url'] not in pick_old]
    main_urls = {c['url'] for c in main_now}

    def prelim(e):
        return (reg_i.get(e['_rg'], 99), e['geo'], e['n247'], -e['h_label'], e['order'])

    # ------------------------------------------------------------ scan
    if a.mode == 'scan':
        cand, seen, rows = [], set(), []
        n_match = sum(len(v) for v in by_brand.values())
        for b in brands:
            es = sorted(by_brand.get(b.n, []), key=prelim)
            keep = [e for e in es if e['url'] in main_urls] + [e for e in es if e['url'] not in main_urls]
            take, rest = [], 0
            for e in keep:
                if has_cred(e['url']) or e['drm']:
                    continue
                if len(take) < a.per_brand or e['url'] in main_urls:
                    take.append(e)
                else:
                    rest += 1
            for e in take:
                if e['url'] not in seen:
                    seen.add(e['url'])
                    cand.append(cinfo(e))
            rg = collections.Counter(e['_rg'] for e in es)
            rows.append((b.n, len(es), dict(rg), len(take), rest))
        (out / 'refill_kandidat.json').write_text(json.dumps(cand, ensure_ascii=False, indent=0), encoding='utf-8')
        L = ['# refill scan', f'Entri dibaca: iptv-org {len(iptv)} + dhanytv/extra {len(dh)} = {len(ents)}',
             f'Merek di katalog: {len(brands)}. Entri yang cocok: {n_match}. URL yang akan dites: {len(cand)} (out/refill_kandidat.json)',
             f'Belum ada status tes lokal: {sum(1 for c in cand if S.local.get(c["url"], {}).get("ok") is None)} dari {len(cand)} URL',
             f'Cocok nama tapi dibuang karena wilayah (mis. Australia, Eropa untuk merek non-Eropa): {sum(skip.values())}', '']
        L.append('## Merek TANPA satu pun entri di sumber (tidak ada yang bisa dinaikkan)')
        L += [f'- {n}' for n, tot, _, _, _ in rows if tot == 0] or ['- (tidak ada)']
        L += ['', '## Merek ditemukan: jumlah entri, wilayah, dites']
        for n, tot, rg, tk, rest in rows:
            if tot:
                L.append(f'- {n}: {tot} entri {rg}, dites {tk}' + (f' (+{rest} di atas batas)' if rest else ''))
        (out / 'refill_scan.txt').write_text('\n'.join(L) + '\n', encoding='utf-8')
        print('\n'.join(L[:5]))
        print(f'  merek tanpa entri: {sum(1 for r in rows if r[1] == 0)} dari {len(rows)}. Detail: out/refill_scan.txt')
        return

    # ------------------------------------------------------------ apply
    picks, rep = [], []
    stats = collections.Counter()
    for b in brands:
        es = by_brand.get(b.n, [])
        covered = [c for c in main_now if b.hit(texts_for(c['name'], c['tvg'], qual)) and S.local.get(c['url'], {}).get('ok') is True]
        if covered:
            stats['COVERED'] += 1
            rep.append((b.n, 'SUDAH ADA (lolos tes)', f'{covered[0]["name"]} -> folder {covered[0]["folder"][:2]}'))
            continue
        if not es:
            stats['NOTFOUND'] += 1
            rep.append((b.n, 'TIDAK ADA DI SUMBER', ''))
            continue
        good = sorted([e for e in es if local_ok(S, e) is True and not e['drm'] and not has_cred(e['url'])],
                      key=lambda e: (reg_i.get(e['_rg'], 99), -S.res(e), e['n247'], e['geo'], e['order']))
        if not good:
            tested = sum(1 for e in es if local_ok(S, e) is not None)
            stats['NOLIVE'] += 1
            cred = sum(1 for e in es if has_cred(e['url']))
            rep.append((b.n, 'TIDAK ADA YANG HIDUP', f'{len(es)} entri, dites {tested}, belum dites {len(es) - tested}' + (f', {cred} berkredensial (dilewati)' if cred else '')))
            continue
        for k, e in enumerate(good[:M.get('keep_per_brand', 1)]):
            label = clean_name(e['name'])
            picks.append(dict(brand=b.n, label=label, folder=b.f, pos=b.idx * 10 + k, url=e['url'], region=e['_rg'],
                              src_name=e['name'], height=S.res(e)))
            rep.append((b.n, 'DINAIKKAN', f'{e["name"]} [{e["_rg"]}] {S.res(e)}p -> {FL[b.f][:2]}'))
        stats['PICK'] += 1
    assert all(p['folder'] in {f['key'] for f in R['folders']} for p in picks), 'folder di major_brands.yml tidak ada di rules.yml'
    (D / 'refill_pick.json').write_text(json.dumps(picks, ensure_ascii=False, indent=1), encoding='utf-8')
    cred_list = [(b, e) for b in brands for e in by_brand.get(b.n, []) if has_cred(e['url'])]
    L = ['# refill laporan', f'Merek: {len(brands)}. Sudah ada: {stats["COVERED"]}, dinaikkan: {stats["PICK"]}, tidak ada yang hidup: {stats["NOLIVE"]}, tidak ada di sumber: {stats["NOTFOUND"]}', '']
    for lab in ('DINAIKKAN', 'TIDAK ADA YANG HIDUP', 'TIDAK ADA DI SUMBER', 'SUDAH ADA (lolos tes)'):
        L.append(f'## {lab}')
        L += [f'- {n}: {d}' if d else f'- {n}' for n, s, d in rep if s == lab] or ['- (kosong)']
        L.append('')
    L.append(f'## Entri berkredensial di URL, tidak pernah dipilih ({len(cred_list)})')
    L += [f'- {b.n}: {e["name"]} ({urlsplit(e["url"]).hostname})' for b, e in cred_list[:40]] or ['- (kosong)']
    (out / 'refill_laporan.txt').write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('\n'.join(L[:2]))
    print('  detail: out/refill_laporan.txt, picks: data/refill_pick.json')


if __name__ == '__main__':
    main()
