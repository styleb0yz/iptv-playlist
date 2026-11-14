# iptv, cara rawat (baca ini dulu)

Satu `playlist.m3u` untuk TiviMate dari iptv-org + dhanytv + sumber tambahan + radio. Dirakit `build.py`, diperbarui harian oleh GitHub (`update.yml`).

## Tiga perintah yang cukup (di Terminal, folder proyek)
- `bash tes_lokal.sh` : build, tes stream URL baru dari jaringan rumah, build ulang. Tambah `semua` untuk tes ulang semuanya (lama; sebulan sekali cukup).
- `bash update_sumber.sh` : tarik sumber terbaru (iptv-org, dhanytv, extra) + id EPG, lalu build. Versi manual dari workflow harian.
- `bash tes_stb.sh` : build, lalu sajikan playlist (tampil URL untuk HP dan TiviMate). Ctrl+C untuk berhenti.
Skrip membuat venv sendiri kalau belum ada. Perintah manual ada di bagian bawah.

## Alur harian (otomatis, setelah GitHub aktif)
tarik sumber -> gabung EPG -> radio -> build tahap 1 -> cek stream (dari GitHub, channel non-Indonesia saja) -> build final -> commit `data/` -> publish ke Pages.
Channel non-Indonesia yang mati otomatis pindah ke folder 70 sendiri. Tetap manual: tes channel Indonesia (`bash tes_lokal.sh`, upload `data/status_lokal.json`), dan edit `rules.yml`.
Kalau jadwal berhenti jalan: tab Actions di repo. GitHub mematikan jadwal repo publik yang tidak ada aktivitas 60 hari; commit harian workflow seharusnya menjaganya, tapi belum terbukti.

## Satu channel, banyak sumber: bagaimana
Build memilih SATU stream terbaik per channel (lolos tes > resolusi > bukan [Not 24/7] > bukan [Geo-blocked]; seri: iptv-org dulu). Itu yang tampil di folder 01-15. Alternatif yang kalah: gagal tes -> folder 70; lolos tapi beda varian (iptv-org) -> folder negara/arsip; dari dhanytv/extra -> hanya dicatat di `out/laporan.md`. Stream yang URL-nya persis sama dibuang dari folder arsip (folder 01-15 tidak pernah dibuang). Pemilihan terjadi saat build, bukan saat nonton: TiviMate tidak memilih sumber sendiri, dan kalau stream utama mati, pengganti baru terpilih di build berikutnya. Belum diverifikasi: apakah TiviMate punya fitur pindah sumber otomatis.

## Menambah M3U lain
1. **File lokal:** taruh di `data/extra/NAMA.m3u`. **Dari URL (diambil harian):** tambah satu baris `nama URL` di `extra_sources.txt`. Atau kirim file/URL-nya ke Claude di chat, nanti dirapikan.
2. Supaya bergabung ke channel yang sudah ada (mis. SCTV), beri `tvg-id` yang SAMA dengan id draft/iptv-org (contoh `tvg-id="SCTV.id"`). Lihat `data/extra/gist_ahmadarif.m3u`. Tanpa tvg-id, dicocokkan lewat nama; beri `group-title="Indonesia Channels"` untuk channel Indonesia.
3. Format M3U biasa: `#EXTM3U`, lalu pasangan `#EXTINF` + URL. Nama channel jangan digabung dengan URL.
4. Setelah itu: `bash tes_lokal.sh`. Entri baru dianggap "belum dites" dan menang sementara atas yang gagal; hasil tes menentukan.

## Memaksa channel tetap di foldernya (walau gagal tes)
`rules.yml` -> `pin:` (nama persis seperti kolom `nama` di `draft_esensial.csv`). Entri bisa tidak bisa diputar. `out/laporan.md` bagian "Pin aktif" menunjukkan status tiap pin.

## EPG
Sekarang hanya satu sumber (dhanytv), cakupan: Indonesia. `rules.yml` -> `epg.sources` untuk menambah (urutan = prioritas); sumber > 1 digabung workflow jadi `site/epg.xml`, lalu ganti `epg.url` ke `https://USER.github.io/iptv-playlist/epg.xml`. Id EPG harus SAMA dengan `tvg-id`. Ukur cakupan: `python3 epg_check.py --epg FILE.xml --playlist out/playlist.m3u --out /tmp/ids.txt`.

## Perintah manual (venv aktif: `source venv/bin/activate`)
- Build: `python3 build.py --index data/index.m3u --dhany data/dhanytv.m3u --draft draft_esensial.csv --dir data --out out --require-radio`
- Tes URL baru: `python3 check_local.py out/kandidat_cek.json -o data/status_lokal.json --workers 8 --per-host 2 --timeout 10 --retries 2 --max-age-hours 99999`
- Status Indonesia: `python3 lihat_status.py`

## Peta file
`build.py` perakit | `check_local.py` tes stream | `fetch_sources.py`/`fetch_radio.py` ambil sumber | `epg_merge.py`/`epg_check.py` EPG | `tes_lokal.sh`/`tes_stb.sh` pembantu |
`rules.yml` aturan | `draft_esensial.csv` folder 01-15 | `data/` input (+ `status_lokal.json`, `extra/`) | `out/` hasil (dibuat ulang) | `docs/` handoff + panduan | `_arsip/` lama.
