# Handoff (nama file tetap, isi selalu terbaru): playlist IPTV untuk TiviMate (iptv-org + dhanytv + sumber tambahan)

Menggantikan v5 dan semua handoff lama. Baca juga `README.md` (cara rawat) dan `docs/SETUP_GITHUB.md`. Diperbarui 14 Nov 2026 (setelah v3 diperiksa ulang).
Akun baru tidak punya memory: semua konteks ada di sini + file di zip.

## 1. Tujuan
Satu M3U untuk TiviMate GRATIS (1 playlist), folder buatan sendiri, TV + radio, update harian lewat GitHub Actions + Pages (repo publik `iptv-playlist`).
Satu channel = satu grup, satu folder, tidak ada yang dibuang. Pemenang: lolos tes lokal > resolusi > bukan [Not 24/7] > bukan [Geo-blocked]; seri -> iptv-org, lalu dhanytv/extra.

## 2. User dan lingkungan
- Gaya: Indonesia kasual (gue/lo), pemula, hemat token, satu batch per balasan, perintah siap copy-paste, user minta Claude bertindak sebagai PM (usul urutan kerja sendiri).
- Mac Apple Silicon. **Folder kerja `~/Downloads/iptv`**. venv tidak bisa dipindah: `python3 -m venv venv && source venv/bin/activate && pip install pyyaml`.
- ISP MyRepublic, Mac 192.168.1.19, STB + TiviMate gratis. Sandbox Claude tanpa internet: tidak boleh klaim stream hidup. Ganti DNS tidak mengubah hasil tes.
- Pelajaran: semua angka di handoff berasal dari sandbox sampai user menjalankannya di Mac. Cocokkan dulu angka build di Mac dengan angka di sini.
- Zip untuk chat baru: `cd ~/Downloads && zip -r iptv_kirim_vN.zip iptv -x "iptv/venv/*" "iptv/out/*" "iptv/_arsip/*" "*/__pycache__/*" "*.DS_Store"` (naikkan N tiap ada perubahan; satu zip saja).

## 3. Struktur
Root: skrip (`build.py`, `check_local.py`, `fetch_sources.py`, `fetch_radio.py`, `epg_merge.py`, `epg_check.py`, `lihat_status.py`, `probe_pluto.py`), `rules.yml`, `draft_esensial.csv`, `extra_sources.txt`, `update.yml`, `README.md`.
`data/` input (index.m3u, dhanytv.m3u, radio_cache.json, epg_ids.txt, status_lokal.json, fetch_status.json, `extra/*.m3u`). `out/` hasil build (tidak masuk zip). `docs/` handoff, SETUP_GITHUB.md, catatan_indonesia.md, epg_hasil.txt, gist_nanti/. `_arsip/` versi lama.
Folder playlist 01-71 (urutan dari rules.yml, jangan diubah): 01 Indonesia National, 02 Indonesia News, 03 Islam, 04 Football & Sports, 05 NBA/Golf/Rugby, 06 Movies & Series, 07 Intl News, 08 Kids, 09 America, 10 UK, 11 Europe, 12 Music, 13 Documentary, 14 TVRI Regional, 15 Radio, 16 Archive Indonesia Local, 17 Pluto, 18 World Religious, 19-59 negara, 60-69 kawasan, 70 Archive Likely Dead, 71 Others.

## 4. Fitur yang ditambah sesi ini (tes: sandbox saja, belum di Mac/GitHub/TiviMate)
- **`pin`** di rules.yml: channel tetap di foldernya walau semua kandidat gagal tes. Aktif untuk: SCTV, Trans TV, Trans7, RRI Net, BeritaSatu, TVRI Sport, Al-Iman TV (Indonesia), Surau TV, Mentari TV. Risiko: sebagian tidak bisa diputar.
- **Sumber tambahan:** `data/extra/*.m3u` dibaca build.py (diperlakukan seperti dhanytv; pakai tvg-id yang sama dengan id iptv-org supaya bergabung ke channel itu). `extra_sources.txt` = daftar `nama URL` yang diambil harian oleh fetch_sources.py (kegagalannya tidak menggagalkan job; kalau gagal pakai salinan kemarin). Teruji dengan file:// dan kasus gagal.
- **Gist ahmadarif (Nov 2023)** sudah masuk sebagai `data/extra/gist_ahmadarif.m3u` (8 URL: SCTV x2, Trans TV, Trans7, RRI Net, BeritaSatu x2, Surau TV). **Belum dites stream**; sementara berstatus "belum dites" sehingga menang atas kandidat yang gagal. Wajib dites di Mac (README).
- **`epg_merge.py`:** gabung beberapa EPG XMLTV (rules.yml `epg.sources`, urutan = prioritas); dipakai update.yml (langkah EPG). Teruji dengan data sintetis, belum dengan EPG asli. Saat ini sumber cuma dhanytv. Sumber tambahan: globetvapp/epg sudah 404; kandidat lain ada di antrian Q4.

- **Dedup URL sama:** entri dengan URL persis sama dibuang dari folder ARSIP (>15), disisakan yang foldernya paling kecil; folder 01-15 tidak pernah dibuang. Dicatat di laporan.md. Efek: 153 entri.
- **laporan.md** kini punya bagian "Pin aktif" (status tiap pin) dan "Dibuang karena URL sama".
- **`tes_lokal.sh`** (tes URL baru / `semua`, lalu build) dan **`tes_stb.sh`** (build + server) = dua perintah rutin user. Teruji di sandbox (tes jaringan gagal karena offline, alurnya jalan).
- **Dry-run workflow di sandbox (offline, sumber file://):** fetch_sources, EPG jalur gagal (fallback, epg_ids.txt tidak berubah) dan jalur sukses (data sintetis), fetch_radio (pakai cache), build tahap 1 dan 2, check_local mode GitHub (offline: dibatalkan oleh guard 70% gagal, status tidak ditulis), siapkan situs. Yang TIDAK teruji: git push, Pages, jaringan asli, durasi cek ~11.800 URL.

## 5. Status terbukti (build sandbox dengan data/status_lokal.json = 252 OK dari 416)
- Tanpa extra+pin (dicek di Mac juga): masuk 12.503, playlist 11.984, duplikat 519, mati 143, draft hilang 0.
- Dengan extra+pin+dedup URL (sandbox): masuk 12.511, playlist 11.835, duplikat 676, mati 136. Folder 01 = 18, 02 = 8. Angka ini bergeser setelah gist dites.
- Format playlist valid (0 EXTINF rusak), header url-tvg ada (EPG dhanytv). Folder 01-14 versi lama: 229 channel semua lolos tes lokal.
- Cakupan EPG: folder 01 13/14, 02 7/7, 14 30/30; folder 05, 06, 09, 10, 11 = 0; radio 1/108. Sesuai opsi A (EPG Indonesia saja). Jadwal dhanytv berakhir 20 Nov 2026.
- Radio: 108 stasiun, hanya 8 pernah dites. 153 URL muncul di lebih dari satu entri (149 lintas folder), 15 entri non-HTTP.
- Koreksi lama: GTV lolos (proxy rctiplus). SCTV/Trans TV/Trans7 sebelumnya tidak punya kandidat lolos; stream SCTV 202.150.172.59 selalu timeout dari jaringan user (mati atau diblokir ISP: belum dibedakan).

## 6. ANTRIAN (urut; centang di sini tiap selesai, jangan ada yang dilewati)
Status: [ ] belum, [~] sebagian, [x] selesai. Yang bertanda "Mac" atau "STB" hanya bisa dikerjakan user.
- [x] Q0 (Mac, 15 Nov, hasil user): folder proyek = `~/Downloads/iptv` (ada). Folder lama dengan hasil tes Q1 ikut terbuang ke Trash sebagai "iptv 1.33.41 PM" (penyebab dugaan: ekstrak zip lewat Finder; belum pasti). Hasil tes lama tidak perlu dipulihkan: `tes_lokal.sh` mengetes ulang URL yang belum dites (8 gist, cepat). Aturan: ekstrak zip lewat Terminal (`unzip -o`), bukan klik dua kali di Finder. Di Mac pakai `python3`, atau `python` hanya setelah `source venv/bin/activate` di folder proyek.
- [x] Q0b (Mac, 15 Nov, hasil user): `update_sumber.sh` + `tes_lokal.sh` jalan penuh di Mac. Sumber: iptv-org 11.472 (+8), dhanytv 950 (+11); `masuk=12530` = 12511+8+11 (semua tambahan terhitung). Setelah tes URL baru: 17 dites, 4 OK, 13 gagal; final playlist=11849, duplikat=681, mati=133. EPG dhanytv tetap: 884 channel, jadwal 11 Nov 16:00 UTC sampai 20 Nov 02:00 UTC (20 Nov 09:00 WIB), tidak berubah di tiga pengukuran (sandbox 2x, Mac 1x), jadi penulis belum memperbarui sejak sekitar 11 Nov; frekuensi sebenarnya belum diketahui. Ini angka acuan baru di Mac.
- [x] Q1 (Mac, 14 Nov, hasil user): angka cocok, `masuk=12511`. Setelah tes: playlist=11831, duplikat=680, mati=133. Semua 8 URL gist GAGAL (timeout), jadi SCTV, Trans TV, Trans7, RRI Net, BeritaSatu, Surau TV hampir pasti tidak bisa diputar; tetap tampil karena di-pin. Penyebab (mati, diblokir ISP, atau geo) belum dibedakan: lihat Q9.
- [ ] Q2 (STB): `bash tes_stb.sh`, buka URL di browser HP, lalu player. Catat: playlist masuk? jadwal RCTI/Metro? radio bunyi? urutan folder? pin (SCTV, Trans TV)? kecepatan load? ada pilihan stream alternatif di TiviMate?
- [ ] Q3 (sekitar 18-19 Nov, SEBELUM habis): ukur ulang jadwal dhanytv: `python3 epg_check.py --epg https://raw.githubusercontent.com/dhasap/dhanytv/main/epg.xml --playlist out/playlist.m3u --out /tmp/x.txt | sed -n 2,4p`. Kalau akhir jadwal masih 20 Nov, EPG Indonesia akan kosong; cari sumber cadangan. Kalau sudah maju, penulis memperbarui berkala.
- [ ] Q4 (Mac): cari dan ukur sumber EPG tambahan untuk folder 05, 06, 09, 10, 11 (sekarang 0): `python3 epg_check.py --epg URL_ATAU_FILE --playlist out/playlist.m3u --out /tmp/ids.txt`, kirim tabelnya. globetvapp/epg SUDAH 404 (dicek user dan sandbox, 14 Nov; halaman cache sempat tampil, jangan dipakai). Kandidat belum diverifikasi: `https://i.mjh.nz/all/epg.xml` (terutama Pluto/Plex/Samsung TV Plus; relevan ke folder 17, bukan stasiun utama) dan `https://dearbulut.github.io/iptv/epg/guide.xml.gz` (berbasis id iptv-org, proyek hobi, keandalan tidak diketahui).
- [ ] Q5: setup GitHub (`docs/SETUP_GITHUB.md`), Run workflow manual sekali. Belum pernah jalan.
- [ ] Q6: setelah Q2, coba OTT Navigator di STB. Kalau failover antar stream jalan, ubah build menyimpan beberapa varian per channel dengan `tvg-id` sama.
- [ ] Q7: putuskan otomasi tes channel Indonesia: launchd di Mac, atau manual bulanan.
- [ ] Q8: setelah 60 hari, pastikan jadwal GitHub tidak mati (heartbeat `data/last_run.txt` belum terbukti dihitung).
- [ ] Q9 (opsional): dedup URL ganda lintas folder 01-15, tes 100 radio, diagnosa SCTV 202.150.172.59 (curl Mac vs HP data seluler), 44 entri cocok EPG tanpa remap, Vietnam 89 ke 86 antar build, durasi cek GitHub ~11.800 URL, `#EXTVLCOPT` dibaca TiviMate atau tidak.
- [x] Sudah (sandbox saja): build direproduksi dari zip bersih, heartbeat di update.yml, mention DRM dan VOD dihapus dari dokumen, handoff digabung.

## 7. Aturan asisten baru
Baca ini + README, ringkas maks 5 baris, tanya hanya yang memblokir. Satu batch per balasan. Tandai jelas terbukti vs dugaan. Jangan ubah urutan folder. Kalau status_lokal.json berubah, build ulang dulu sebelum menilai isi folder. build.py menimpa out/laporan.md tiap jalan.

## 8. Keputusan dan temuan sesi 14 Nov (zip v3 diperiksa ulang di sandbox)
- **Terbukti di sandbox (build ulang dari zip bersih):** masuk=12511, playlist=11835, duplikat=676, mati=136, dibuang URL sama=153. Sama dengan bagian 5. Belum terbukti di Mac.
- **Sumber:** iptv-org = repo komunitas berisi sekitar 11.000 URL stream publik gratis. dhanytv = M3U + EPG kurasi satu orang, fokus Indonesia (EPG-nya yang dipakai `url-tvg`). Radio dari Radio Browser. Semua stream milik pihak ketiga, tanpa jaminan hidup.
- **Failover antar stream:** belum terkonfirmasi di TiviMate. Kandidat pengganti: OTT Navigator (Android TV). Changelog lama (beta 1.6.8.1) menyebut fold duplicate channel dan opsi untuk tidak pindah source otomatis saat error, jadi fiturnya kemungkinan ada. Belum dites di STB, dan belum dipastikan UI-nya lebih bersih. Konsekuensi: build harus menyimpan beberapa varian per channel dengan `tvg-id` sama. Putuskan sesudah Tes 1 dan satu tes OTT Navigator.
- **Hosting dan otomasi:** tetap GitHub Actions + Pages. Cloudflare gratis diduga tidak cocok untuk tes sekitar 11.800 URL (batas CPU dan jumlah permintaan Workers; dugaan, belum dicek di dokumentasi).
- **Heartbeat:** `update.yml` kini menulis `data/last_run.txt` tiap run supaya selalu ada commit harian. Sebelumnya commit hanya terjadi kalau data berubah. Belum terbukti bahwa commit bot dihitung sebagai aktivitas oleh GitHub.
- **EPG dhanytv (diukur 14 Nov dari sandbox):** jadwal 11 Nov 16:00 UTC sampai 20 Nov 02:00 UTC, 884 channel. Awal jadwal 11 Nov menunjukkan file tidak diperbarui tiap hari; frekuensi sebenarnya belum diketahui (riwayat commit tidak terbaca dari sandbox). Playlist memakai URL raw-nya langsung, jadi kalau penulis memperbarui, TiviMate ikut tanpa tindakan. Kalau tidak, jadwal Indonesia kosong setelah 20 Nov.
- **EPG folder 01-15 (epg_check 14 Nov, dhanytv saja):** 01 = 17/18, 02 = 7/8, 03 = 6/16, 04 = 3/25, 05 = 0/15, 06 = 0/33, 07 = 1/23, 08 = 4/13, 09 = 0/28, 10 = 0/1, 11 = 0/9, 12 = 1/9, 13 = 1/10, 14 = 30/30, 15 = 1/108. Kekosongan ada di folder non-Indonesia, jadi butuh sumber tambahan (Q4).
- **Maintenance:** harian 0 (setelah GitHub terbukti). Bulanan opsional: `bash tes_lokal.sh`, upload `data/status_lokal.json`. Playlist berhenti update: buka tab Actions, salin error, kirim ke Claude bersama template di bawah. Nol maintenance mutlak tidak realistis karena sumber gratis bisa berubah atau hilang.
- **Tes channel Indonesia:** harus dari jaringan rumah (GitHub runner di luar Indonesia). Opsi otomatis: launchd di Mac (Mac harus menyala), atau VPS berIP Indonesia (berbiaya). Belum diputuskan.

## 9. Template prompt untuk chat atau akun baru (hemat token)
Upload zip terbaru saja, jangan tempel riwayat chat. Lalu:
```
Lanjutkan proyek IPTV. Baca docs/handoff-iptv.md dan README.md di zip terlampir dulu.
Aturan: satu langkah per balasan, Indonesia kasual, hemat token, tandai jelas terbukti vs dugaan, jangan tinggalkan hasil di sandbox. Semua hasil dikemas jadi satu zip iptv_kirim_vN.zip (naikkan versi).
Tugas sekarang: <satu tugas, atau tempel error / angka build>
```

## 10. Aturan agar tidak hilang
Sandbox Claude sementara. Yang dihitung hanya file yang disajikan sebagai unduhan dan sudah diunduh user: selalu satu zip `iptv_kirim_vN.zip`. Tiap sesi baru: unggah zip terbaru, kerjakan satu item antrian, hasilkan zip baru.

## 11. Apa yang otomatis ikut pembaruan sumber (dan apa yang tidak)
- **EPG dhanytv (jadwal):** header playlist `url-tvg` menunjuk langsung ke `raw.githubusercontent.com/dhasap/dhanytv/main/epg.xml`. Kalau penulis memperbarui, TiviMate ikut tanpa tindakan kita.
- **`data/epg_ids.txt`:** snapshot id yang punya jadwal. build.py memakainya untuk memetakan `tvg-id`. Basi kalau dhanytv menambah atau mengganti id. Diperbarui otomatis oleh workflow GitHub (setelah aktif), atau manual: `python3 epg_check.py --epg https://raw.githubusercontent.com/dhasap/dhanytv/main/epg.xml --playlist out/playlist.m3u --out data/epg_ids.txt`.
- **`data/dhanytv.m3u` dan `data/index.m3u` (daftar channel):** snapshot di zip. Ikut penulis kalau `fetch_sources.py` jalan: harian di GitHub (Q5), atau manual lewat `bash update_sumber.sh` (Q0b).
- Jadi: "dhanytv update, kita ikut" benar untuk jadwal EPG sekarang, dan untuk daftar channel hanya setelah GitHub aktif.

## 12. Protokol kerja (berlaku tiap sesi)
1. Satu zip `iptv_kirim_vN.zip` untuk semua hasil. Sandbox sementara; yang dihitung cuma yang sudah diunduh user.
2. Tiap balasan yang mengubah sesuatu: perbarui antrian (bagian 6) di handoff, naikkan N, kirim zip baru.
3. Tandai tiap klaim: TERBUKTI (di mana: sandbox, Mac, STB) atau DUGAAN. Jangan menyebut sesuatu beres kalau belum dites.
4. Isi halaman web bisa berasal dari cache. Kalau user melaporkan hasil nyata (mis. 404), hasil user yang menang.
5. Jawab per poin, urut, jelaskan yang tumpang tindih. Hemat token: jangan ulangi isi yang sudah ada di handoff.
6. Item yang belum jelas konteksnya masuk antrian, jangan dilewati.
7. Ekstrak zip lewat Terminal, bukan Finder. Zip dari Claude berisi `data/status_lokal.json` versi sandbox. Sebelum `unzip -o` di Mac, cadangkan punya user (`cp iptv/data/status_lokal.json /tmp/`) lalu kembalikan sesudahnya, atau hasil tes Mac tertimpa. Untuk chat baru, kirim zip yang dibuat dari folder Mac (perintah di bagian 2) supaya hasil tes ikut.

## Catatan Q4 (14 Nov, Mac) - sebagian, belum selesai
- i.mjh.nz/all/epg.xml: 289 channel AU/NZ, 0 cocok (format ID `mjh-xx`). dearbulut guide: 404. iptv-org.github.io/epg/guides/* (4 alamat): 404.
- tvg-id playlist = ID iptv-org (`Nama.us@feed`). iptv-org.github.io/api/guides.json memetakan channel -> site + site_id.
- Folder 05, 06, 09, 10, 11 (86 channel): 75 punya site di guides.json. 30 terbukti punya jadwal di i.mjh.nz (05=7, 06=18, 09=5, 10=0, 11=0). ID EPG = bagian setelah `#` di site_id. Alamat file: i.mjh.nz/<Layanan>/<wilayah>.xml (hidup: Plex/au,ca,es,fr,gb,mx,nz,us; PlutoTV/ar,br,cl,de,es,fr,gb,mx,us; Roku/all; SamsungTVPlus/us. Flash/epg kosong).
- Jadwal pendek: Pluto sekitar 1 hari, Plex/Roku sekitar 3 hari, SamsungTV+ habis 14 Nov 17:00 UTC. Perlu tarik ulang harian (otomatis, Q5).
- Sisa 45 channel: sumbernya tvtv.us, tvguide.com, tvpassport.com, sky.com, tv24.se, tv.sfr.fr, hanya lewat pengambil sendiri (iptv-org/epg). 11 channel tanpa sumber (tetap di playlist tanpa jadwal).
- Belum: cek dukungan remap ID di epg_merge.py/rules.yml; putuskan sumber untuk 45 channel.

## Catatan Q4 lanjutan (14 Nov, Mac)
- epg_merge.py (62 baris) dibaca: gabung per id persis, sumber pertama menang, tanpa pemetaan ID. update.yml: epg_merge -> epg_check -> data/epg_ids.txt. rules.yml: epg.mode=single, url-tvg playlist = dhanytv.
- build.py baris 348-403 punya hook EPG (epg_ids) dan menulis "Remap tvg-id: N entri" (baris 400). Isinya BELUM dibaca: cek dulu apakah remap itu bisa dipakai untuk ID i.mjh.nz.
- EPG gabungan baru terpakai di STB kalau Q5 (GitHub Pages) jalan, lalu epg.url di rules.yml diganti.
- Langkah berikutnya: baca build.py baris 340-380, putuskan pemetaan ID (hash i.mjh.nz -> tvg-id) + filter channel; baru Q2 (tes STB).

## 0. ATURAN KERJA (kunci; mengalahkan aturan lama di bagian lain, terutama "satu langkah per balasan" dan "zip dari sandbox")
- Bahasa Indonesia kasual (gue/lo). Hemat token. Tanya konteks dulu sebelum mulai.
- Kerja per fase: pahami, riset, tes. Jangan mulai fase berikutnya sebelum user bilang "go".
- Perintah terminal: jelaskan tiap bagian (fungsi, tahap proses, output yang diharapkan), gabung dalam satu blok.
- Hal yang tumpang tindih dijelaskan satu per satu, tidak ada yang di-skip. Tandai jelas: terbukti vs dugaan.
- Handoff harus selalu siap pindah chat atau akun (limit bisa habis kapan saja). Tiap blok perintah yang menghasilkan temuan diawali dengan menambahkan catatan temuan sebelumnya ke docs/handoff-iptv.md. Akhir tiap balasan ada ringkasan "Catatan handoff".
- Folder ~/Downloads/iptv di Mac = sumber kebenaran. Zip untuk chat baru dibuat user di Mac: `bash ~/Downloads/iptv/kirim.sh` (menghapus zip lama, membuat satu zip baru). Jangan ekstrak zip di Mac. Jangan membuat zip di sandbox.
- Pesan pembuka chat baru (3 baris): lihat bagian paling ujung file ini, "Pesan pembuka".

## Pesan pembuka (tempel ke chat baru bersama zip terbaru)
Lanjutkan proyek IPTV. Baca docs/handoff-iptv.md di zip, mulai dari bagian "0. ATURAN KERJA" (di ujung file) dan ikuti, lalu README.md. Tanya konteks yang kurang sebelum mulai.
Posisi: lihat "Catatan Q4" di ujung handoff. Q4 sebagian selesai, berikutnya baca build.py baris 340-380 soal remap tvg-id.
- kirim.sh terbukti jalan di Mac (14 Nov 14:26): zip 694 KB, 3 file kunci ikut.
- kirim.sh terbukti jalan di Mac (14 Nov 14:26): zip 694 KB, 3 file kunci ikut.
- build.py out_tvg (baris 354-368) dibaca: "remap" hanya memilih varian tvg-id milik channel itu sendiri (tvg asli, tanpa @feed dan awalan auto., tvg anggota grup duplikat) yang ada di data/epg_ids.txt. Tidak ada tabel pemetaan, tidak bisa memetakan MLB.us ke hash i.mjh.nz. (terbukti dari kode)
- Desain usulan (belum diputuskan): data/epg_map.json (id iptv-org -> id i.mjh.nz, dari guides.json) + epg_merge.py mengganti id sumber mjh jadi id iptv-org dan menyaring hanya channel terpetakan (ukuran). Playlist tetap pakai id iptv-org.
- Q2 tidak bergantung EPG baru (hanya url-tvg). Tersisa riset: update.yml + docs/SETUP_GITHUB.md (Q5), kelayakan pengambil iptv-org/epg untuk 45 channel.

## Keputusan user (14 Nov): desain EPG disetujui
- Fase A: data/epg_map.json (id i.mjh.nz -> id iptv-org tanpa @feed) + epg_merge.py mengganti dan menyaring id. build.py out_tvg akan memilih id tanpa @feed itu dari epg_ids.txt (inferensi dari kode, belum dicoba).
- Fase B (nanti): 45 channel lewat pengambil iptv-org/epg (Node). update.yml saat ini Python saja, belum ada setup-node. Belum terbukti sumbernya bisa diakses dari GitHub Actions.
- Q2 (tes STB) tidak bergantung pada EPG baru.

## Keputusan user (14 Nov): desain EPG disetujui
- Fase A: data/epg_map.json (id i.mjh.nz -> id iptv-org tanpa @feed) + epg_merge.py mengganti dan menyaring id. build.py out_tvg akan memilih id tanpa @feed itu dari epg_ids.txt (inferensi dari kode, belum dicoba).
- Fase B (nanti): 45 channel lewat pengambil iptv-org/epg (Node). update.yml saat ini Python saja, belum ada setup-node. Belum terbukti sumbernya bisa diakses dari GitHub Actions.
- Q2 (tes STB) tidak bergantung pada EPG baru.

## Hasil A1 (14 Nov, Mac): buat_epg_map.py
- 145 pasangan, 57 channel iptv-org (folder 01-15) punya jadwal di i.mjh.nz: 04=5/25, 05=7/15, 06=18/33, 07=11/23, 08=2/13, 09=5/27, 12=4/9, 13=5/10; 01, 02, 03, 10, 11, 15 = 0. 05/06/09 cocok dengan Q4.
- Masalah: Plex/us 0 dari 23 (dugaan: awalan id Plex di guides.json beda dengan XML, cocokkan lewat hash setelah '-'); Foxtel/epg jadwal habis 18 Okt (basi); Flash/epg 404.
- Horizon jadwal: Pluto sekitar 22 jam, SamsungTV+ sekitar 12 jam, Plex dan Roku sekitar 3 hari, SkyGo sampai Feb 2027, au/* sampai 30 Nov. Cron update.yml sekali sehari (20:30 UTC); dugaan: kurang untuk Pluto/Samsung (belum diukur).
- update.yml: EPG pakai continue-on-error, deploy Pages. SETUP_GITHUB.md: repo Public, belum pernah dijalankan.
- Desain direvisi: epg_merge.py tidak diubah. epg_mjh.py membuat XMLTV lokal (id iptv-org, acara yang belum lewat saja) lalu didaftarkan di rules.yml epg.sources. Urutan prioritas dhanytv vs mjh untuk id dobel: belum diputuskan.

## Hasil A2 (14 Nov, Mac): epg_mjh.py
- /tmp/epg_mjh.xml: 57 channel, 5975 acara, 4600 KB. Plex/us kini dipakai untuk 6 channel (perbaikan hash jalan). Cakupan folder 01-15 tetap 57 (07: 11->10 karena NHKWorldJapan.jp hanya ada di Foxtel yang basi; 09: 5->6).
- epg_check: persis 0 karena id mjh tanpa @feed dan playlist lama masih id asli; remap 105 (output terpotong head -30, 3 baris arsip tidak terlihat).
- Horizon per channel terpakai (14:37 WIB): Plex 40-66 jam, Roku 70-78, Pluto 15-17, SkyGo 137-724. Angka lama Pluto 22 jam = maks seluruh file, bukan channel terpakai.
- Overlap dhanytv x mjh: 3 id (AlJazeera.qa, FIFAPlus.uk, beINSPORTSXTRA.us), bentuk id beda (@feed), jadi prioritas di epg_merge tidak berpengaruh; build.py out_tvg memilih tvg asli dulu (dari kode, belum dicoba).
- MASALAH: update.yml langkah EPG (baris 33) jalan sebelum build tahap 1 (baris 46), jadi out/playlist.m3u belum ada di GitHub dan epg_mjh.py gagal diam-diam (continue-on-error). Usul: pindah langkah EPG ke setelah build tahap 1.
- Belum: 18 pasangan tanpa acara belum dirinci; frekuensi update i.mjh.nz belum diukur; 2 channel Samsung-only (Stadium.us, VICETV.us) nasibnya belum jelas.

## Hasil A2b (14 Nov 14:49 WIB, Mac)
- epg_mjh.py dipatch di Mac (cetak channel per sumber + alasan pasangan tanpa acara). Run ulang: 57 channel, 5967 acara, 4595 KB (8 acara lebih sedikit dari A2 = acara yang selesai dalam 12 menit).
- Selisih channel A1 vs A2 (terbukti dari daftar): +IONTV.us (09, dari Plex/us), -NHKWorldJapan.jp (07, hanya ada di Foxtel basi). Total 57 sama.
- Samsung TV+ tidak dipilih untuk channel mana pun karena jadwalnya lebih pendek (sekitar 11 jam) dari sumber lain; Stadium.us dan VICETV.us kini dari Plex/us. Bukan hilang.
- 18 pasangan tanpa acara: 6 Foxtel (jadwal habis), 12 'id tidak ada di file' (Plex/es 4, PlutoTV/cl 3, PlutoTV/gb 2, Roku/all 2, Plex/us 1). 17 dari 18 channelnya tetap dapat jadwal dari sumber lain; hanya NHKWorldJapan.jp yang hilang. Penyebab id tidak ada: dugaan mapping guides.json basi.
- Plex/us: hash cocok untuk sekitar 22 dari 23 pasangan (inferensi). Cek nama channel: 56 dari 57 cocok; NOWRock.uk tampil sebagai "That's Rock" (folder 12), dugaan rename, dibiarkan.
- epg_check: 3 remap yang tadi terpotong ada di folder 62 (Archive MENA); 105 = 102 + 3.
- i.mjh.nz tidak mengirim last-modified; header age cuma umur cache CDN (17-38 menit). Frekuensi update belum terukur. Rencana: jalankan epg_mjh.py | head -12 sekitar 21:00 dan 03:30 WIB, bandingkan horizon Pluto.
- Berikutnya (A3, tunggu go): tes lokal gabungan di temp dulu, baru ubah update.yml dan rules.yml.

## Hasil A3 tes lokal (14 Nov, Mac)
- Merge dhanytv + mjh: 941 channel (884 + 57), 26216 acara. Acara mjh 5967 di file, 5946 setelah merge (21 dibuang dedupe channel+start; penyebab dugaan duplikat di sumber).
- Build di salinan data (/tmp): masuk=12530 playlist=11849 duplikat=681 sama dengan Mac. Remap tvg-id 65 -> 166 (prediksi sandbox tepat). Selisih baris selain tvg-id = 0. Sandbox: dari 101 entri yang berubah, 0 yang sebelumnya cocok dhanytv (tidak ada regresi).
- Cakupan folder 01-15 (persis = remap): 01=17, 02=7, 03=6, 04=6, 05=7, 06=18, 07=11, 08=6, 09=6, 10=0, 11=0, 12=5, 13=6, 14=30, 15=1. Total 126/346 (sebelumnya 71/346); TV 01-14: 125/238.
- epg_check: kolom remap = kumulatif (persis + normalisasi), bukan hanya yang di-remap. 105 vs +101: 4 entri id overlap (beIN XTRA 04, FIFA+ 04, AlJazeera@Arabic 62 x2) sudah cocok dhanytv persis. 'Sisa jadwal 30.2 hari' = acara terjauh (SkyGo), bukan dhanytv; dhanytv tetap habis 20 Nov 02:00 UTC (Q3).
- Arsip (16+): persis < remap = Q9 '44 entri' = beda varian @feed (mis. 48Hours.us@CA vs @US), tidak diremap, dibiarkan.
- PERINGATAN: tvg-id hasil remap (id mjh) hanya ada jadwalnya di EPG gabungan; url-tvg masih dhanytv saja. Manfaat di TiviMate baru muncul setelah url-tvg ke epg.xml gabungan (Pages/Q5, atau serve lokal). update_sumber.sh (manual) tetap dhanytv saja dan menimpa epg_ids.txt tanpa id mjh.
- Berikutnya: A3b edit update.yml (langkah EPG dipindah ke setelah Build tahap 1 + epg_mjh.py) dan rules.yml (sumber kedua /tmp/epg_mjh.xml).

## Hasil A3b-A3e (14 Nov, Mac)
- update.yml: langkah EPG sudah setelah Build tahap 1 (urutan 4-9 dicek); rules.yml sumber ke-2 /tmp/epg_mjh.xml. Backup di _arsip/*.sebelum-a3b.
- update.yml punya permissions contents/pages/id-token write; step Simpan data commit data/ (epg_ids.txt ikut). Siapkan situs tidak menghapus site/.
- i.mjh.nz/X.xml = 302 ke raw.githubusercontent.com/matthuisman/i.mjh.nz/master/X.xml. Header age bukan umur file. Plex/us.xml.gz 2.5 MB vs .xml 16.2 MB (belum dipakai).
- epg_merge: sumber hilang dilewati; semua hilang exit 1 (terbukti). Risiko terbuka: dhanytv gagal + mjh sukses menimpa epg_ids.txt dengan 57 id.
- GitHub API 403 rate limit; frekuensi update i.mjh.nz belum terukur. Tidak ada venv/ dan .gitignore; SETUP_GITHUB.md ada di docs/.

## Hasil A3b-A3f (14 Nov, Mac)
- update.yml: langkah EPG setelah Build tahap 1 (urutan dicek); rules.yml sumber ke-2 /tmp/epg_mjh.xml; backup _arsip/*.sebelum-a3b. permissions contents/pages/id-token write; Simpan data commit data/; Siapkan situs tidak menghapus site/.
- i.mjh.nz/X.xml = 302 ke raw.githubusercontent.com/matthuisman/i.mjh.nz/master/X.xml; header age bukan umur file. Plex/us.xml.gz 2.5 MB vs .xml 16.2 MB; get() di epg_mjh.py sudah gunzip.
- epg_merge: sumber hilang dilewati, semua hilang exit 1 (terbukti). Risiko terbuka: dhanytv gagal + mjh sukses menimpa epg_ids.txt dengan 57 id (usul P2).
- Commit i.mjh.nz (WIB, 14 Nov): Pluto/Plex/Roku ~tiap 3 jam (07:44, 10:44, 13:40), Samsung ~tiap jam. Dugaan: cron 03:30 membuat Pluto kosong ~17:40-19:40 WIB sampai build berikut. Belum terbukti.
- 21 duplikat channel+start di epg_mjh.xml = 5967-5946 (terbukti); penyebab di epg_mjh.py belum jelas.
- SETUP_GITHUB.md ada di docs/ (14 baris); .github/ dibuat manual lewat web; docs/ ikut ke repo Public kecuali di-exclude.

## Hasil A2b-A3g (14 Nov, Mac)
- Plex/us: 6 channel = GravitasMovies, HallmarkMoviesMore, IONTV, Stadium, VICETV, beINSPORTSXTRA. Stadium dan VICETV tidak hilang (dugaan Samsung-only gugur).
- Cek nama id vs display-name: 57 channel, 1 beda: NOWRock.uk tampil 'That's Rock' (28 acara); sisanya cocok.
- 12 pasangan tanpa acara (non-Foxtel): semua 'id tidak ada di file' (mapping cadangan basi); channelnya punya sumber lain yang jalan. 6 pasangan Foxtel basi; NHKWorldJapan.jp tidak punya sumber lain.
- Flash/epg.xml = 404 (302 ke raw.githubusercontent.com lalu 404). 4 channel hanya bermapping Flash/epg dan tanpa jadwal: CNN.us (09), NHKWorldJapan.jp (07, juga Foxtel basi), TRTWorld.tr (07), i24NEWSEnglishWorld.il (07). 5 channel lain bermapping Flash (termasuk NBCNewsNOW) dapat jadwal dari sumber lain.
- Pluto menyuplai 19 dari 57 channel; horizon Pluto 14-16 jam (sekitar 15:45 WIB), turun dari 15-17 jam (14:37).
- Cakupan EPG mjh per folder: 04=5/25 05=7/15 06=18/33 07=10/23 08=2/13 09=6/27 12=4/9 13=5/10; total 57 channel, 5894 acara.
- Upload web GitHub: 31 file, data 3.0M, docs 48K, tidak ada file >20MB, tidak ada .DS_Store.
- Belum: konfirmasi commit i.mjh.nz ~16:40 WIB (pola 3 jam Pluto/Plex/Roku), keputusan P1/P2/P3, keputusan cron, Q5 setup GitHub.

## P2 (14 Nov, Mac): penjaga epg_ids
- epg_guard.py baru (root): tolak epg_ids.new kalau kosong atau < 80% jumlah id epg_ids.txt lama; file lama tidak ada = lolos. update.yml langkah EPG: guard dipasang sebelum mv. Backup _arsip/update.yml.sebelum-p2.
- Batas: guard hanya melindungi epg_ids.txt. site/epg.xml tetap ter-deploy apa adanya (kalau dhanytv gagal, EPG di Pages cuma isi mjh). Ambang 80% angka tebakan. Belum dijalankan di Actions.
- Flash/epg.xml 404 (tidak ada folder Flash di repo i.mjh.nz); cek commit ~16:40 WIB belum dilakukan (cek terakhir 15:47 WIB, masih 13:40).

## Q5 setup GitHub (14 Nov, Mac + browser)
- Repo styleb0yz/iptv-playlist (Public). Upload 31 file via web (folder ~/Downloads/iptv-upload, tanpa update.yml dan docs/handoff-iptv.md). .github/workflows/update.yml dibuat manual (commit 7b19ad2). Pages Source = GitHub Actions. Run manual #1 hijau, 14m14s.
- Hasil Pages: playlist.m3u 11849 channel, epg.xml 941 channel (884 dhanytv + 57 mjh), 26093 acara, id mjh ada. Runner GitHub BISA akses i.mjh.nz (terbukti). Guard P2 lolos (941 vs 884).
- Header url-tvg playlist masih dhanytv. Edit rules.yml epg.url -> https://styleb0yz.github.io/iptv-playlist/epg.xml sudah dibuat di Mac (backup _arsip/rules.yml.sebelum-epgurl). Upload ke GitHub BELUM terkonfirmasi (raw rules.yml masih dhanytv). Setelah ke-upload: Run workflow lagi, cek baris pertama playlist, lalu tambah playlist ke TiviMate (https://styleb0yz.github.io/iptv-playlist/playlist.m3u).
- Belum: cek commit i.mjh.nz setelah 16:45 WIB (pola 3 jam), keputusan cron (Pluto 19 channel habis jadwal ~17:40-19:40 WIB dengan cron 03:30), Q2 tes STB, Q3 ukur jadwal dhanytv 18-19 Nov (habis 20 Nov), Fase B (folder 10/11, 4 channel tanpa jadwal: CNN.us, NHKWorldJapan.jp, TRTWorld.tr, i24NEWSEnglishWorld.il).

## STATUS TERBARU UNTUK CHAT BARU (14 Nov 2026) <- BACA INI DULU
SELESAI (terbukti dari output Mac / run Actions):
- EPG mjh: epg_mjh.py, tes lokal A2/A2b/A3 (57 channel; cakupan TV folder 01-14 naik 29% -> 53% di EPG gabungan).
- update.yml: langkah EPG dipindah ke setelah Build tahap 1. P2: epg_guard.py (tolak epg_ids.new kalau kosong atau <80% dari lama).
- GitHub: repo styleb0yz/iptv-playlist, 31 file terunggah, workflow dibuat, Pages hidup, run #1 hijau (14m14s). epg.xml di Pages 941 channel termasuk id mjh.
URUTAN LANJUT:
1. rules.yml epg.url -> https://styleb0yz.github.io/iptv-playlist/epg.xml: edit sudah ada di Mac (backup _arsip/rules.yml.sebelum-epgurl). Di GitHub BELUM terkonfirmasi (raw rules.yml masih dhasap/dhanytv; cek dengan git clone, bukan raw karena cache). Setelah ke-upload: Run workflow #2, cek baris 1 playlist.m3u, lalu tambah https://styleb0yz.github.io/iptv-playlist/playlist.m3u ke TiviMate.
2. Cek commit i.mjh.nz (clone dangkal, jam WIB): dugaan Pluto/Plex/Roku tiap 3 jam, Samsung tiap jam (data 14 Nov: commit 07:44, 10:44, 13:40). Dari situ putuskan cron (dugaan: 19 channel Pluto kosong ~17:40-19:40 WIB dengan cron 03:30).
3. Q2 tes STB (tes_stb.sh). Q3 ukur jadwal dhanytv 18-19 Nov (habis 20 Nov 02:00 UTC). Fase B (folder 10/11; 4 channel tanpa jadwal mjh: CNN.us, NHKWorldJapan.jp, TRTWorld.tr, i24NEWSEnglishWorld.il). Q6-Q9.
RISIKO/CATATAN: guard hanya melindungi epg_ids.txt; site/ dibangun ulang tiap run, kalau EPG gagal total Pages tanpa epg.xml sampai build berikut. Flash/epg.xml 404 di i.mjh.nz. Repo Public. update_sumber.sh (manual) tetap dhanytv saja.
CARA KERJA DENGAN USER: user copy-paste perintah tanpa baca jawaban panjang. Taruh 'Aksi lo' paling atas, SATU blok perintah per pesan, tandai TERBUKTI vs DUGAAN, jangan ubah file proyek sebelum user bilang 'go'. Handoff ini sendiri berantakan (blok dobel, aturan bagian 0 vs 7/10/12); rapikan kalau user mau.

## Hasil langkah 1 (14 Nov, Mac, cek git clone)
- GitHub rules.yml baris 12 masih dhasap/dhanytv/main/epg.xml (TERBUKTI, commit terakhir e55025f 16:45 WIB). Edit epg.url ke Pages ada di Mac tapi belum ke-upload.
- Berikutnya: upload rules.yml via web, cek ulang dengan git clone, Run workflow #2, cek baris 1 playlist.m3u, tambah ke TiviMate.

## Hasil langkah 1b (14 Nov, Mac, cek git clone)
- rules.yml di GitHub sudah epg.url = Pages (commit b541743 16:55 WIB), SAMA PERSIS dengan Mac. TERBUKTI.
- Run workflow #2 hijau 49 dtk. Header url-tvg playlist = https://styleb0yz.github.io/iptv-playlist/epg.xml, 11849 channel, epg.xml HTTP 200 dan 941 channel. TERBUKTI. Commit d4227a2 16:57 WIB dari run #2.
- status_github.json 11044 URL (7900 OK), semua bertanda jam 09 UTC. DUGAAN: run #2 cepat karena --max-age-hours 20 melewati URL yang baru dites run #1.
- Berikutnya: langkah 2 (commit i.mjh.nz untuk cron), TiviMate (Q2).

## Hasil cron 3x (14 Nov, Mac)
- Commit i.mjh.nz 14 Nov: Pluto/Plex/Roku sekitar tiap 3 jam (07:05, 07:44, 10:44, 13:40, 16:37 WIB), Samsung tiap jam. TERBUKTI untuk jendela 10 jam, pola malam DUGAAN.
- update.yml di Mac: cron jadi '30 20,4,12 * * *' UTC = 03:30, 11:30, 19:30 WIB. Backup _arsip/update.yml.sebelum-cron. Tujuan: Pluto (19 channel, horizon sekitar 14-16 jam) tidak kosong malam hari. DUGAAN, belum terbukti.
- Di GitHub BELUM diubah: .github/workflows/update.yml harus diedit lewat web (baris 5). Cek dengan git clone setelah itu.

## Hasil cron 3x terverifikasi (14 Nov 17:04 WIB, Mac, git clone)
- GitHub .github/workflows/update.yml = cron '30 20,4,12 * * *' (commit 4aa0b2c), SAMA PERSIS dengan Mac. TERBUKTI.
- Run terjadwal pertama dengan jadwal baru: 19:30 WIB 14 Nov (jadwal GitHub bisa telat). Cek: git clone, log harus ada commit data baru dan data/last_run.txt berubah. BELUM terbukti.
- Berikutnya: TiviMate (Q2) dengan https://styleb0yz.github.io/iptv-playlist/playlist.m3u, Q3 ukur jadwal dhanytv 18-19 Nov, Fase B (folder 10/11).

## STATUS TERBARU v2 (14 Nov 2026, setelah 17:04 WIB) <- BACA INI DULU. MENGGANTIKAN "STATUS TERBARU UNTUK CHAT BARU" dan "Pesan pembuka" di atas (keduanya sudah usang)
SELESAI (TERBUKTI dari output Mac / git clone):
- Langkah 1: rules.yml di GitHub epg.url = https://styleb0yz.github.io/iptv-playlist/epg.xml (commit b541743 16:55 WIB), SAMA PERSIS dengan Mac.
- Run workflow #2 hijau 49 dtk (commit d4227a2 16:57 WIB). playlist.m3u baris 1 url-tvg = Pages, 11849 channel, epg.xml HTTP 200 dan 941 channel. status_github.json 11044 URL (7900 OK), semua bertanda jam 09 UTC. Penyebab 49 dtk = DUGAAN: --max-age-hours 20 melewati URL yang baru dites run #1.
- Cron GitHub = '30 20,4,12 * * *' UTC (03:30, 11:30, 19:30 WIB), commit 4aa0b2c 17:04 WIB, SAMA PERSIS dengan update.yml di Mac (backup _arsip/update.yml.sebelum-cron). Alasan: i.mjh.nz Pluto/Plex/Roku update sekitar tiap 3 jam (07:05, 07:44, 10:44, 13:40, 16:37 WIB; TERBUKTI untuk jendela 10 jam, malam DUGAAN), horizon Pluto 14-16 jam, cron lama sekali sehari membuat 19 channel Pluto kosong sekitar 17:40-03:30 WIB (DUGAAN).
BELUM:
- TiviMate di STB (Q2) belum dicoba. URL: https://styleb0yz.github.io/iptv-playlist/playlist.m3u
- Run terjadwal pertama jadwal baru (19:30 WIB 14 Nov) belum terbukti. Cek: git clone, harus ada commit data baru dan data/last_run.txt berubah.
URUTAN LANJUT:
1. Hasil TiviMate (Q2): playlist masuk atau tidak, waktu load, urutan folder 01-71, jadwal RCTI dan Metro, radio (folder 15), SCTV dan Trans TV (pin) tampil dan bisa diputar atau tidak, ada stream alternatif atau tidak.
2. Cek run terjadwal 19:30 WIB.
3. Q3: ukur jadwal dhanytv sekitar 18-19 Nov (habis 20 Nov 02:00 UTC).
4. Fase B: folder 10/11 dan 4 channel tanpa jadwal (CNN.us, NHKWorldJapan.jp, TRTWorld.tr, i24NEWSEnglishWorld.il).
5. Q6-Q9.
PERINGATAN:
- zsh di Mac: komentar # dengan tanda kurung di blok perintah bikin parse error. Blok perintah harus tanpa komentar.
- data/ di GitHub lebih baru dari Mac (bot commit tiap run: status_github.json, epg_ids.txt, fetch_status.json, radio_cache.json, index.m3u, dhanytv.m3u, last_run.txt). Jangan upload ulang seluruh data/. Untuk hasil tes Mac upload HANYA data/status_lokal.json. Folder Mac tidak punya status_github.json, dan build.py membacanya (baris 152), jadi angka build Mac vs GitHub bisa beda (DUGAAN, belum diuji; angka acuan keduanya 11849).
- Repo Public: jangan upload docs/handoff-iptv.md (isinya IP LAN dan ISP) ke repo. update.yml di root Mac = isi .github/workflows/update.yml di GitHub; edit lewat web lalu cocokkan pakai diff.
- Cek GitHub pakai git clone, bukan raw (cache).
- Zip untuk chat baru: bash ~/Downloads/iptv/kirim.sh (tanpa venv, out, _arsip). Jangan ekstrak zip lewat Finder.
- Handoff ini berantakan (blok dobel, bagian 0 vs 7/10/12). Bagian 0 ATURAN KERJA menang. Rapikan hanya kalau user minta.
PESAN PEMBUKA TERBARU (tempel ke chat baru bersama zip):
Lanjutkan proyek IPTV. Baca docs/handoff-iptv.md di zip, mulai dari bagian STATUS TERBARU v2 (paling ujung file), lalu 0. ATURAN KERJA, lalu README.md. Tanya konteks yang kurang sebelum mulai.
Posisi: cron 3x sehari aktif, playlist Pages hidup (11849 channel, EPG gabungan). Berikutnya hasil TiviMate Q2 dan cek run 19:30 WIB.
Aturan: gue/lo kasual, Aksi lo di atas, satu blok perintah per pesan tanpa komentar, tandai TERBUKTI vs DUGAAN, jangan ubah file sebelum gue bilang go.

## Hasil Fase B riset (14 Nov, sandbox + web, belum dites di Mac atau GitHub)
- iptv-org/epg = aplikasi Node (npm install, lalu npm run grab dengan --channels dan --output). maxConnections default 1. README sendiri bilang di bawah beban berat situs bisa error atau memblokir. TERBUKTI dari README.
- tvtv.us: issue #3187 (3 Jul 2026) melaporkan situs memblokir akses data guide. Diskusi #1604 (31 Jul 2026) mengecek endpoint langsung dan dapat 404. Tahun 2024 sempat 403. Jadi tidak bisa diandalkan. TERBUKTI dari halaman GitHub, tapi itu laporan orang lain, bukan tes kita.
- tvguide.com: 403 di issue Des 2024 sampai Jan 2025 (sudah ditutup). Status Nov 2026 tidak diketahui.
- tvpassport.com: ada issue fitur Agu 2026 yang dibalas maintainer 23 Okt 2026 bahwa grabber memakai atribut gambar dari situs. Menyiratkan grabber jalan, tapi bukan bukti dari IP GitHub. DUGAAN.
- Komunitas iptv-org boleh menerbitkan guide.xml sendiri (daftar di GUIDES.md, id iptv-org). Contoh worker StrangeDrVN/epg: 466 channel, 40 MB, 73 channel kosong (termasuk 5 dari 10 channel tvtv.us). Alternatif tanpa scraping sendiri: pakai guide worker sebagai sumber ke-3 di epg_merge. Cakupan untuk channel kita belum diukur, keandalan satu orang tidak diketahui.
- Belum: daftar channel tanpa jadwal per site (skrip fase_b.py), uji grabber di Actions.

## Hasil Fase B ukur (14 Nov, Mac, EPG Pages vs playlist Pages vs guides.json)
- 112 channel unik folder 01-14 tanpa jadwal di EPG gabungan (941 id). Per folder tanpa jadwal/total: 01=1/18, 02=1/8, 03=10/16, 04=19/25, 05=8/15, 06=15/33, 07=12/23, 08=7/13, 09=21/28, 10=1/1, 11=9/9, 12=4/9, 13=4/10, 14=0/30. TERBUKTI.
- 24 channel tidak punya site apa pun di guides.json (tidak ada grabber). Site terbanyak: tvtv.us 36, tvpassport.com 31, tvguide.com 30, sky.com 21, epg.iptvx.one 17, tv.blue.ch 14 (satu channel bisa ada di beberapa site, jadi tidak boleh dijumlah). TERBUKTI.
- tvtv.us dilaporkan rusak (issue #3187, diskusi #1604) dan tvguide.com pernah 403, jadi kelompok itu berisiko. Detail per channel: docs/fase_b_hasil.txt.
- Berikutnya: Q2 TiviMate (STB harus di jaringan rumah MyRepublic), lalu lanjut Fase B.

## Hasil Fase B ukur 2 (14 Nov, Mac)
- Dari 112 channel tanpa jadwal: 86 punya site selain tvtv.us dan tvguide.com, 2 hanya punya tvtv.us atau tvguide.com, 24 tanpa site. TERBUKTI. Punya site BUKAN bukti site itu jalan dari IP GitHub (mapping mjh dulu juga basi di 12 pasangan).
- Folder 01-03 tanpa jadwal (11): 01 IndonesianaTV.id (tanpa site); 02 BeritaSatu.id (cubmu, dens.tv, maxstream.tv, vidio.com); 03 AlBahjahTV.id, AlImanTV.id, IqraaQuran.sa, QatarTVTheHolyQuran.qa, PeaceTVEnglish.ae (tanpa site), RodjaTV.id (dens.tv, maxstream.tv), NabawiTV.id (cubmu.com), MQTV.id (maxstream.tv), AlSunnahAlNabawiyahTV.sa (dens.tv, shahid.mbc.net), AlQuranAlKareemTV.sa (6 site). TERBUKTI.
- Berikutnya: cari 11 channel itu lewat nama di epg.xml Pages (mungkin ada dengan id lain di dhanytv), lalu Q2 di STB, lalu putuskan pilot grabber.

## Hasil Fase B cari nama dan posisi STB (14 Nov, Mac)
- Koreksi: channel folder 01-03 tanpa jadwal ada 12 (01=1, 02=1, 03=10), bukan 11 seperti di catatan sebelumnya.
- Cari nama di epg.xml Pages: hanya 2 dari 12 yang punya kecocokan nama: BTV.id@SD (Berita Satu DensTV, 3 acara) dan id "Indonesiana TV" (ChannelFeed, 3 acara). PeaceTVChinese.ae@SD adalah channel lain, bukan Peace TV English. 10 channel lain tidak ada di EPG sama sekali. TERBUKTI. Dua kecocokan itu 3 acara saja, DUGAAN placeholder.
- Jadi remap tidak menyelesaikan folder 01-03. Sisanya butuh grabber (site Indonesia: vidio.com, dens.tv, maxstream.tv, cubmu.com) atau diterima tanpa jadwal.
- Posisi STB: user di depan TV, STB terhubung lewat hotspot iPhone (setelan router ribet untuk debugging wifi). Alamat Wireless debugging STB DUGAAN 172.20.10.10:39133. Q2 di hotspot: hasil putar stream mewakili jaringan seluler, bukan MyRepublic.

## Hasil adb STB (14 Nov, Mac)
- adb terpasang (platform-tools 37.0.1) dan terhubung ke 172.20.10.10:39133: model B866F_V1_1, product oppen. TERBUKTI.
- Ukuran unduhan TiviMate: playlist.m3u 2.965.848 byte, epg.xml 10.009.848 byte (curl tanpa kompresi, transfer sebenarnya bisa lebih kecil, DUGAAN).
- Rencana Q2: semua langkah lewat adb saat STB masih di hotspot (cek paket, reset data atau pasang APK, ketik URL), lalu STB pindah ke WiFi rumah MyRepublic untuk tes stream.

## STATUS TERBARU v3 (14 Nov 2026, sekitar 17:30 WIB) <- BACA INI DULU, menggantikan v2 untuk posisi terakhir
SELESAI: semua yang ada di v2, ditambah Fase B riset dan ukur. 112 channel folder 01-14 tanpa jadwal; 86 punya site selain tvtv.us dan tvguide.com; 24 tanpa site. Folder 01-03: 12 channel tanpa jadwal, pencarian nama di EPG tidak menolong (2 kecocokan cuma 3 acara). Detail: docs/fase_b_hasil.txt. tvtv.us dilaporkan rusak (issue #3187). TERBUKTI dari output Mac atau halaman GitHub.
POSISI Q2 (sedang jalan): user di depan TV, STB model B866F_V1_1 di hotspot iPhone, adb terhubung ke 172.20.10.10:39133 (TERBUKTI). Perintah adb tanpa -s gagal: more than one device/emulator. Pakai adb devices -l lalu adb -s 172.20.10.10:39133 ... TiviMate di STB error (jenis error belum diketahui). APK ada di ~/Downloads/tivimate.apk, 21122308 byte, sha256 beaebb25bf818450bf496d4cefb16885b190f156815dea280c31eaae0909ee6c (sumber APK belum diverifikasi, pastikan resmi). Rencana: cek paket ar.tvplayer.tv (nama paket DUGAAN), adb shell pm clear dulu, kalau gagal reinstall, tambah playlist https://styleb0yz.github.io/iptv-playlist/playlist.m3u, lalu pindahkan STB ke WiFi rumah MyRepublic untuk tes stream (hasil di hotspot tidak mewakili stream Indonesia).
BELUM: hasil Q2, run terjadwal 19:30 WIB (cek git clone), Q3 (18-19 Nov), pilot grabber Fase B, rapikan handoff, Q6-Q9.
PESAN PEMBUKA: sama dengan v2, tapi posisinya Q2 sedang jalan (adb ke STB).

## Hasil adb cek paket (14 Nov 17:27, Mac)
- adb devices menampilkan STB dua kali (172.20.10.10:39133 dan nama mDNS adb-ZTEATV49300480509-26Fu0k), model sama B866F_V1_1: satu perangkat, dua entri. Pakai adb -s 172.20.10.10:39133. TERBUKTI.
- TiviMate terpasang: paket ar.tvplayer.tv, versionName 2.1.5, versionCode 2151, update terakhir 2026-11-13 21:14:33. Android 14, CPU armeabi-v7a (32-bit), ruang /data sekitar 23,7 GB bebas. TERBUKTI. Versi APK di Mac belum dicek.
- Berikutnya: tangkap log crash (logcat) SEBELUM pm clear atau reinstall, lalu tambah playlist, lalu pindah STB ke WiFi rumah MyRepublic.

## Q2 17:31 log crash dan keputusan
- logcat -b crash kosong, tidak ada FATAL setelah launch TiviMate 2.1.5, MainActivity fokus. TERBUKTI. Screenshot STB cuma 10610 byte (kemungkinan layar kosong, DUGAAN).
- User putuskan: uninstall TiviMate lalu install APK ~/Downloads/tivimate.apk via adb, tambah playlist, lalu lanjut fase lain.

## Q2 17:40 reinstall TiviMate
- Uninstall ar.tvplayer.tv Success, install ~/Downloads/tivimate.apk Success. sha256 cocok dengan catatan v3 (beaebb25...ee6c). Terpasang: versionName 5.3.3, versionCode 1000005332, targetSdk 34. TERBUKTI.
- Versi lama sebelumnya 2.1.5 (versionCode 2151), tidak cocok dengan riwayat rilis TiviMate resmi. DUGAAN: itu build non-resmi atau rusak.
- Pencarian web: APKMirror mencatat TiviMate 5.3.3 diunggah 23 Juni 2026 (ukuran 10,20 MB), paket ar.tvplayer.tv. Ukuran APK di Mac 21122308 byte (sekitar 20,1 MB), jadi tidak sama dengan 10,20 MB itu. Keaslian APK BELUM terbukti, DUGAAN beda varian.

## Q2 17:48 layar baru
- TiviMate 5.3.3 terpasang ulang, installerPackageName=null (dipasang via adb), apkSigningVersion=3. Screenshot sekarang 83041 byte, beda dengan sebelumnya yang 10610 byte. TERBUKTI. Isi layar belum dibaca.
- Hash signatures=71648878 bukan sidik jari sertifikat, tidak bisa dipakai membuktikan keaslian APK.

## Q2 17:52 layar playlist
- uiautomator dump berhasil. TiviMate 5.3.3 ada di layar tambah playlist M3U: tombol Enter URL, Paste from clipboard, Select local playlist, Back, Next. TERBUKTI. Instal ulang menyelesaikan error lama (app sekarang tampil normal).
- Berikutnya: isi URL https://styleb0yz.github.io/iptv-playlist/playlist.m3u via adb input text.

## Q2 17:58 playlist masuk
- URL playlist terketik benar di field TiviMate (terbukti dari uiautomator). User tekan Next: TiviMate memproses 11844 channel dan 5 movies, lalu lanjut ke EPG (laporan user, belum dicek lewat adb). Posisi STB masih di hotspot iPhone, stream belum dites.
- Berikutnya: pindah STB ke WiFi rumah MyRepublic, sambung ulang adb (IP dan port berubah), lalu tes stream Indonesia.

## Q2 18:05 pindah WiFi
- Dump layar: STB di home launcher (CleanYourTV UI), TiviMate muncul di home. TERBUKTI. Dump itu kemungkinan diambil sebelum pindah WiFi (DUGAAN, karena adb ke IP hotspot masih jalan).
- User lapor STB sudah pindah ke WiFi MyRepublic. IP dan port adb berubah, perlu sambung ulang. Mac harus di WiFi yang sama.

## Q2 18:20 ide dan catatan user (WAJIB dicatat)
- adb ke 172.20.10.10:39133 status offline. STB sudah dipindah ke WiFi MyRepublic, Mac masih di 172.20.10.9 (hotspot). User di lantai atas, STB di bawah: sesi adb berhenti sampai user di dekat STB lagi. TERBUKTI (offline) / DUGAAN (sebabnya pindah jaringan).
- Hasil scroll user di TiviMate: channel lokal banyak yang jalan, beberapa belum (nama channel TIDAK dicatat user), channel luar banyak yang bagus. EPG belum diperiksa. Laporan user, belum terbukti lewat log.
- IDE 1: nama folder tanpa nomor 01, 02, dst. Catatan teknis: nomor sekarang dibuat otomatis build.py dari urutan di rules.yml (folders lalu archive). Belum dicek apakah TiviMate menjaga urutan grup tanpa nomor (DUGAAN: tidak pasti). Perlu keputusan user, jangan ubah dulu.
- IDE 2: STB dibeli dengan app IPTV lokal dan playlist dari penjual. Banyak yang mati setelah beberapa minggu, ada yang diperbarui. User tanya layak diambil sebagai sumber (grab playlist) atau tidak. Perlu nama app dan URL playlist dari user nanti. Cek dulu asal dan lisensinya sebelum masuk playlist publik.
- Tanpa STB bisa: lihat_status.py (status tes channel Indonesia), tes_lokal.sh dari WiFi rumah, Q3, cek run 19:30, pilot grabber Fase B, rapikan handoff, desain penamaan folder. Dengan STB: cek EPG di layar, tes putar per channel, cek pin.

## Q2 18:35 Mac di MyRepublic
- User lapor Mac sudah di WiFi MyRepublic (lantai atas), SSID sama dengan STB (lantai bawah). Laporan user, IP Mac belum dicek. Output lihat_status.py dari 18:20 belum diterima di chat (hanya perintahnya yang ketempel).
- Berikutnya: cek IP Mac, cari STB lewat adb mdns, sambung ulang, lalu lihat_status.py.

## Q2 18:45 status channel ID
- Mac di 192.168.1.19, gateway 192.168.1.1 (jaringan rumah). TERBUKTI. adb mdns services kosong dan adb devices kosong: STB belum terlihat dari Mac. Sebab belum diketahui (DUGAAN: Wireless debugging mati atau port berubah setelah pindah WiFi, atau AP isolation).
- lihat_status.py: 77 OK, 59 GAGAL dari 136 channel Indonesia (data status_lokal.json lama, jaringan pengetesan lama tidak tercatat). TERBUKTI. Daftar GAGAL belum dilihat (head -70 hanya menampilkan OK).

## Q2 19:00 analisis GAGAL
- 59 channel Indonesia GAGAL (data status_lokal.json lama, jaringan pengetesan tidak tercatat). Alasan: HTTP 404 (flashcon DensTV, ikitv.sqn.at, malingtv, Vision+ untuk Indosiar, MDTV, SCTV), HTTP 429 (r-plus.sedotcw3.workers.dev), timeout (202.150.172.59), DNS gagal Errno 8 (swiftserve [Geo-blocked]), 403 (indihometv, 119.82.250.109), 451 (malingtv). TERBUKTI dari output.
- SCTV: semua varian yang ada GAGAL, tidak ada satu pun OK. TERBUKTI dari daftar OK dan GAGAL. Nasional lain (RCTI, Indosiar, ANTV, GTV/Global, MNC TV, Trans TV, Trans7, TVOne, Kompas, Metro, TVRI) masih punya minimal satu varian OK.
- 429 pada r-plus workers.dev DUGAAN rate limit karena tes paralel, belum dites ulang. arp -a belum menampilkan STB (192.168.1.10 dan .18 incomplete). User turun ke STB untuk baca IP:port Wireless debugging.

## Q2 19:15 sumber penjual dan mode Mac
- "Off STB" = kerja di Mac dulu tanpa sambung ke STB. adb devices kosong, mdns kosong, STB belum terlihat dari Mac. TERBUKTI.
- Playlist dan app IPTV bawaan penjual STB (dibeli sudah terpasang, banyak yang mati setelah beberapa minggu, ada yang diperbarui) belum ada URL atau nama app di handoff, extra_sources.txt masih kosong. Calon sumber untuk menambal channel gagal, terutama SCTV. Butuh URL atau nama app dari user, asal dan lisensi dicek dulu.

## Q2 19:30 rencana grab app penjual
- grep SCTV di data/index.m3u: hanya satu entri Indonesia (SCTV.id@SD, http://202.150.172.59/SCTV/tracks-v1a1/mono.m3u8, tes lokal timeout). Entri SCTV2 sampai SCTV20 itu Vietnam (.vn), bukan SCTV Indonesia. Varian lain dari dhanytv dan gist (Vision+, flashcon, metube, indostreamingtv, indihometv) semuanya GAGAL di data lama. TERBUKTI. Jadi tidak ada SCTV yang hidup di sumber sekarang.
- Keputusan user: playlist penjual diambil LANGSUNG dari app di STB via adb (bukan minta URL ke user). Banyak app di STB, jadi urutannya: (1) adb shell pm list packages -3 untuk daftar app, (2) user tandai mana app dari penjual, (3) cari URL playlist dan EPG di app itu, (4) masukkan lewat protokol biasa: file di data/extra/NAMA.m3u atau baris di extra_sources.txt, tvg-id disamakan, EPG lewat rules.yml epg.sources. Ditunda sampai user di STB dan adb tersambung. Cek asal dan lisensi sebelum masuk playlist publik. Belum ada yang dieksekusi.
- User khawatir limit habis: handoff sudah diperbarui, zip dibuat lewat kirim.sh.
- Kerja Mac berikutnya (butuh go): bash tes_lokal.sh semua dari WiFi rumah, menulis data/status_lokal.json.

## Q2 lanjutan root dan folder
- User bilang STB sudah di-root. Handoff lama tidak pernah mencatat root, jadi ini klaim user, belum terbukti. Cek nanti saat adb tersambung: adb -s IP:PORT shell su -c id (hasil uid=0 berarti root). Kalau root, URL playlist app penjual bisa dibaca dari /data/data/NAMA_PAKET (shared_prefs atau database), tanpa menyadap trafik. DUGAAN, belum dites.
- Rename folder tanpa nomor: BELUM dikerjakan, menunggu go. Penomoran dibuat build.py baris 229 sampai 245 (format {i:02d} · label, termasuk Archive dan folder dead/other). Kunci csv di rules.yml dan draft_esensial.csv memakai teks bernomor, jadi tidak ikut berubah kalau yang diubah hanya format output build.py.
- Risiko rename (DUGAAN, belum dites): tanpa nomor, urutan grup di TiviMate bisa berubah (urutan playlist atau alfabet). Tes dulu dengan playlist kecil sebelum build penuh.
- Jangan upload docs/handoff-iptv.md ke repo publik (berisi IP LAN dan ISP).

## Q2 rencana rename folder (belum dikerjakan, menunggu go)
- TEMUAN TERBUKTI dari kode: build.py memakai int(group[:2]) untuk mengurutkan di baris 312, 368, 403, 439. Kalau nomor dihapus di sumbernya (rules.yml, penomoran baris 229-245), build crash. Jangan hapus nomor di sana.
- Titik tulis tunggal group-title: build.py baris 131. Rencana: nomor tetap dipakai internal untuk urutan, lalu dibuang hanya saat menulis group-title (regex ^\d{2} · ). Urutan file playlist tetap, laporan.md tetap bernomor.
- epg_check.py baris 129 dan 134 membaca nomor dari out/playlist.m3u (g.startswith(('0','1')) dan g[:2].isdigit()). Setelah rename, tabel cakupan folder dan daftar channel tanpa jadwal di skrip itu tidak akurat lagi (hanya laporan, tidak crash, DUGAAN). Perlu penyesuaian kecil.
- DUGAAN belum dites: TiviMate mengurutkan grup sesuai urutan di playlist. Tes lewat bash tes_stb.sh sebelum publish.

## Q2 go rename dijalankan
- User bilang go rename. Patch: build.py fungsi extinf membuang awalan NN · dari group-title (nomor internal tetap, urutan tetap), epg_check.py memakai urutan kemunculan grup di playlist (15 grup pertama = esensial). Backup di _arsip/*.sebelum-rename. Patch sudah diuji di salinan sandbox dari zip 18:19: build OK 11849 entri, group-title tanpa nomor, 0 sisa yang bernomor. TERBUKTI di sandbox, belum di Mac. Urutan grup di TiviMate belum dites (DUGAAN).

## Q2 rename selesai di Mac
- Patch rename dijalankan di Mac: patch ok, build OK masuk=12530 playlist=11849 duplikat=681 ditahan=0, group-title tanpa nomor, urutan dari Indonesia · National TV sampai Radio lalu Archive, sisa group-title bernomor 0. TERBUKTI dari output Mac. Backup: _arsip/build.py.sebelum-rename dan _arsip/epg_check.py.sebelum-rename.
- Angka build di Mac (mati=133, playlist=11849) sama persis dengan hasil sandbox dari zip 18:19. DUGAAN: hasil tes_lokal semua belum menghasilkan data baru (belum selesai, tidak jalan, atau hasilnya sama). Cek lewat tanggal data/status_lokal.json.
- Belum terbukti: urutan grup di TiviMate (butuh bash tes_stb.sh dan layar TV). Playlist online di GitHub masih versi bernomor sampai build.py dan epg_check.py baru diunggah ke repo (DUGAAN: workflow memakai skrip dari repo).

## Q2 tes_lokal semua belum jalan
- 18:37 WIB: data/status_lokal.json masih bertanggal 13:47 hari ini, lihat_status.py tetap 77 OK dan 59 GAGAL. Jadi bash tes_lokal.sh semua yang dikirim sebelumnya tidak menghasilkan data baru (TERBUKTI dari tanggal file). Sebab belum diketahui (DUGAAN: tidak sempat jalan atau terhenti).
- Kandidat hanya 431 URL (136 Indonesia) per build di sandbox, jadi tes ulang seharusnya hitungan menit, bukan jam (DUGAAN, belum diukur).
- Mac sekarang di 192.168.1.x (jaringan rumah MyRepublic). Jalankan ulang dengan log di /tmp/tes_lokal.log.

## Q2 audit folder utama kurang isi (analisis sandbox dari zip 18:19, build lama; belum dijalankan di Mac)
- Rencana draft vs terpasang di folder utama: Film & Series 51 jadi 33, America 42 jadi 28, UK 14 jadi 1 (hanya S4C), Europe 20 jadi 9, Bola 42 jadi 25, NBA/Golf/Rugby 25 jadi 15, Dokumenter 17 jadi 10, Musik 13 jadi 9, Berita Internasional 29 jadi 23. 108 channel draft gagal tes dan masuk Likely Dead. TERBUKTI dari out/audit_esensial.txt.
- Penyebab TERBUKTI: yang dites hanya 431 URL (entri folder utama, gap, Likely Dead). Isi Archive tidak pernah dites (status BELUM), dan build tidak otomatis menaikkan pengganti dari Archive ke slot yang mati. Daftar alt di audit memakai kecocokan nama kasar (contoh: Channel 4 menghasilkan Channel 44, NBC menghasilkan CNBC), jadi 40 slot yang tampak punya alt kebanyakan bukan pengganti sungguhan.
- UK: 13 dari 14 gagal, alasan 403 (BBC One, Two, Three, Scotland, Parliament) dan DNS Errno 8 (ITV2/3/4, Channel 4/5, E4, 5USA). DUGAAN: 403 itu geo-block dari Indonesia. Varian BBC One di Archive UK semuanya berlabel [Geo-blocked].
- HBO: HBO (United States) dan HBO Hits di Likely Dead (aynascope.net, 404). Di Archive ada HBO Asia HD, HBO Family Asia HD, HBO Hits Asia HD, HBO Signature Asia HD (grup Southeast Asia, host 202.150.165.66:8088), semuanya BELUM dites. Calon utama pengganti karena dekat Indonesia (DUGAAN, belum dites).
- Showtime: hanya Showtime Family Zone (OK, folder Film). FX: tidak ada FX US yang layak di sumber. Sony: Sony Movies (United States), Cine Sony, Sony Channel Andes, Sony Movies Latin America ada di Archive United States, BELUM dites. WB: Warner Channel Colombia, Warner Channel South, Warner TV Asia di Archive, BELUM dites.
- Entri HBO Family di Archive Others (aflaxtv.xyz) berisi kredensial di path URL. Jangan jadikan sumber, dan pertimbangkan dibuang dari playlist publik.
- Penomoran masih tampil di TiviMate karena playlist online di GitHub masih build lama. DUGAAN, perlu unggah skrip baru dan refresh playlist di TiviMate.
- Usulan (belum dikerjakan, menunggu go): skrip refill, untuk tiap slot draft yang mati ambil varian merek yang sama (urutan prioritas: Asia, Latin America, US), tes dari WiFi rumah, naikkan yang OK ke folder utama, dan tulis laporan. Plus tambah Sony, WB, HBO Family, Showtime ke draft.

## Hasil refill.sh (14 Nov malam, Mac, WiFi rumah 192.168.1.19) TERBUKTI dari output Mac
- Scan: 12430 entri dibaca, 385 cocok, 353 URL kandidat (229 belum dites), 31 dibuang karena wilayah, 34 merek tanpa entri.
- Tes: 148 OK, 81 gagal. Merek 176: sudah ada 66, dinaikkan 46, tidak ada yang hidup 30, tidak ada di sumber 34.
- Build final: masuk=12530 playlist=11850 duplikat=680 mati=213 (sebelumnya mati=133).
- Dinaikkan sekitar 15 varian Latin America (DUGAAN audio Spanyol atau Portugis, belum dicek).
- Gagal semua (DUGAAN geo-block, belum dibedakan): BBC One sampai Four, BBC Scotland, BBC Parliament, ITV2-4, Channel 4, Channel 5, E4, More4, GB News, France 2, Canale 5, La 1 TVE, NBC, FOX.
- BELUM: upload ke GitHub, keputusan varian Latin America, keputusan nomor folder, tes putar di STB.
- build.py Mac = patch refill + strip nomor di group-title. Jangan ditimpa dengan build.py dari zip.
- Backup status lama: /tmp/status_lokal.sebelum-refill.json. Log: /tmp/refill_log.txt.
- Keputusan user (14 Nov malam): upload ke GitHub DITUNDA (build.py Mac menghapus nomor folder, belum dites di STB). Latin America: user tanya geser ke urutan bawah, folder tetap sama. Belum diubah, menunggu go.

## STATUS TERBARU v4 (14 Nov 2026 malam) <- BACA INI DULU, menggantikan v3 dan semua pesan pembuka lama
SELESAI (TERBUKTI dari output Mac):
- refill.sh dipasang dan dijalankan di Mac (WiFi rumah 192.168.1.19). Hasil: 148 OK, 81 gagal, 46 merek dinaikkan, 66 sudah ada, 30 tidak ada yang hidup, 34 tidak ada di sumber. Build: masuk=12530 playlist=11850 duplikat=680 mati=213. Detail: docs/refill_laporan.txt dan docs/refill_scan.txt (salinan dari out/, karena out/ tidak ikut zip).
- build.py di Mac = patch refill ditambah modifikasi user (strip nomor folder di group-title). JANGAN ditimpa dengan build.py dari zip lama. Backup: _arsip/build.py.sebelum-refill.
- data/status_lokal.json dan data/refill_pick.json di Mac adalah yang terbaru. Backup status lama: /tmp/status_lokal.sebelum-refill.json (sementara).
KEPUTUSAN USER:
- Upload ke GitHub DITUNDA (build.py Mac menghapus nomor folder, belum dites di STB, urutan grup tanpa nomor di TiviMate belum terbukti).
- Latin America diprioritaskan paling bawah; UK, US, Asia tetap diterima. Urutan diserahkan ke Claude (PM). Usulan: region_order di major_brands.yml jadi [asia, us, uk, eu, other, latam]. allowed_regions TIDAK diubah. BELUM dijalankan, menunggu kata "go" dari user.
- Rencana setelah go: edit satu baris region_order di Mac, bash refill.sh lagi (tes stream tidak diulang karena status tersimpan), bandingkan berapa varian [latam] berubah di out/refill_laporan.txt.
BELUM (urut):
1. Go region_order (di atas).
2. Q2 STB: adb ke STB offline sejak STB pindah ke WiFi rumah. User perlu baca IP:port Wireless debugging di STB. Lalu tes putar, EPG, pin, varian [latam] (audio?).
3. Cek run terjadwal 19:30 WIB 14 Nov dan berikutnya: git clone, harus ada commit data baru dan data/last_run.txt berubah.
4. Q3 sekitar 18-19 Nov: ukur jadwal dhanytv (habis 20 Nov 02:00 UTC).
5. Putuskan nomor folder (ide 1) dan jadwal upload ke GitHub: build.py, data/status_lokal.json, data/refill_pick.json saja, bukan seluruh data/.
6. Entri HBO dari aflaxtv.xyz berisi kredensial di URL: pertimbangkan dibuang dari playlist publik.
7. Ide 2: grab playlist app bawaan penjual STB lewat adb (pm list packages -3), cek asal dan lisensi dulu.
8. Fase B (folder 10 dan 11, 4 channel tanpa jadwal), Q6-Q9.
CATATAN: 30 merek gagal tes mayoritas UK dan Eropa (BBC, ITV, Channel 4, France 2, Canale 5, La 1) plus NBC dan FOX. DUGAAN geo-block dari Indonesia, belum dibedakan. Lolos tes di Mac belum berarti jalan di TiviMate. Memory lama bilang dhanytv di-drop, tapi build dan EPG saat ini masih memakai dhanytv: ikuti handoff.
PESAN PEMBUKA v4 (tempel ke chat baru bersama zip terbaru):
Lanjutkan proyek IPTV. Baca docs/handoff-iptv.md di zip, mulai dari bagian STATUS TERBARU v4 (paling ujung file), lalu 0. ATURAN KERJA, lalu README.md. Tanya konteks yang kurang sebelum mulai. Posisi: refill selesai di Mac, upload GitHub ditunda, menunggu go untuk region_order. Aturan: gue/lo kasual, hemat token, Aksi lo di atas, satu blok perintah per pesan tanpa komentar, jelaskan tiap perintah, tandai TERBUKTI vs DUGAAN, kerja per fase dan jangan ubah file sebelum gue bilang go, handoff selalu siap pindah.

## Inventaris Downloads (14 Nov malam, Mac) TERBUKTI dari output Mac
- Aktif: ~/Downloads/iptv (13M, tanpa venv, python3 sistem punya pyyaml). Zip terbaru: iptv_kirim_1411_2020.zip.
- Basi: ~/Downloads/iptv-upload (salinan upload GitHub 15:49), update.yml.untuk-github. Buatan user: ARSIP/ dan ARSIP.zip. Belum dilihat: New Folder With Items, ~/tv/iptv, ~/epg.
- Trash berisi (jangan dikosongkan): iptv, iptv 1.03.20 PM, iptv 1.33.41 PM, iptv-1, iptv_kirim.zip, v3, v4, v5 lama, v7, iptv.zip, tivimate.apk (21122308 byte, APK yang terpasang di STB).
- kirim.sh memakai rm -f (hapus PERMANEN): menghapus iptv_kirim_v5.zip 19:46 (728971 byte, handoff 378 baris). Dipulihkan lewat chat sebagai iptv_kirim_v5_PULIHAN.zip. Jangan jalankan kirim.sh sebelum diperbaiki (Fase 2: zip lama dipindah ke ~/IPTV_BACKUP/zip).
- Belum terverifikasi: apakah handoff Mac punya bagian v5 (Q2 19:15, Q2 19:30, Q2 audit, Q2 refill).
- zsh: find dengan kurung harus di-escape.

## Inventaris lanjutan (14 Nov malam, Mac) TERBUKTI dari output Mac
- Trash otomatis kosong tiap 30 hari: defaults FXRemoveOldTrashItems = 1. Item Trash bertanggal 14 Nov, paling cepat habis sekitar 14 Des. Pindahkan tivimate.apk dan isi Trash yang berguna sebelum itu.
- ~/tv = proyek lain CleanYourTV UI (cleanyourtv-ui, fw, keys.sh, venv-anim, backup). Bukan IPTV, jangan disentuh, keys.sh jangan masuk zip atau GitHub.
- ~/epg = clone iptv-org/epg (sisa riset Fase B). ~/Downloads/New Folder With Items = DUGAAN aset animasi CleanYourTV (ECCO, BRIAN, DELTA, YB), jangan dihapus. ~/Downloads/ARSIP = iptv_merged.zip, iptv.zip, New Folder With Items 2.zip (buatan user, simpan).
- Handoff Mac (436 baris) tidak punya bagian "Q2 refill merek mayor" dari v5; diperiksa baris demi baris dengan v5 PULIHAN.

## Dipulihkan dari v5 (baris yang belum ada di handoff Mac)
- [ ] Q10 (Mac, WiFi rumah): `bash refill.sh` (isi ulang folder utama dengan merek mayor dari semua entri sumber), baca `out/refill_laporan.txt`, upload `build.py` + `data/status_lokal.json` + `data/refill_pick.json` ke repo GitHub, refresh playlist di TiviMate. Detail di blok "Q2 refill merek mayor" di bawah.
- Rencana draft vs terpasang di folder utama: Film & Series 51 jadi 33, America 42 jadi 28, UK 14 jadi 1 (hanya S4C), Europe 20 jadi 9, Bola 42 jadi 25, NBA/Golf/Rugby 25 jadi 15, Dokumenter 17 jadi 10, Musik 13 jadi 9, Berita Internasional 29 jadi 23. 108 channel draft gagal tes dan masuk Likely Dead. TERBUKTI dari out/audit_esensial.txt dan dari build ulang di sandbox (angka folder sama).
- Penyebab TERBUKTI: yang dites hanya entri folder utama, gap, dan Likely Dead. Isi Archive tidak pernah dites, dan build tidak menaikkan pengganti dari Archive ke slot yang mati.
- UK: 13 dari 14 gagal (403 dan DNS Errno 8). DUGAAN: 403 itu geo-block dari Indonesia.
- Entri HBO, HBO Hits, HBO Family dari aflaxtv.xyz berisi kredensial di path URL (pola /USER/PASS/ID). Jangan jadikan sumber, pertimbangkan dibuang dari playlist publik.
- Penomoran masih tampil di TiviMate karena playlist online di GitHub masih build lama. DUGAAN, perlu unggah build baru dan refresh playlist di TiviMate.
## Q2 refill merek mayor (14 Nov, sandbox; belum dijalankan di Mac)
- Yang dibuat: `major_brands.yml` (katalog 176 merek mayor, dua kata kunci: alias nama persis + wilayah yang diterima), `refill.py` (scan dan apply), `refill.sh` (satu perintah), patch kecil di `build.py` (membaca `data/refill_pick.json`; entri pilihan dipindah ke folder utama, kalau gagal tes tetap ke Likely Dead). draft_esensial.csv dan rules.yml tidak diubah.
- Scan TERBUKTI membaca SEMUA entri: iptv-org 11.472 + dhanytv/extra 958 = 12.430. Cocok nama dan wilayah: 385 entri, 368 URL kandidat, 243 di antaranya belum pernah dites. Pencocokan nama persis (alias + sufiks seperti HD, Asia, Latin America), jadi "Channel 4" tidak menarik "Channel 44" dan "NBC" tidak menarik "CNBC".
- Tidak ada satu pun varian yang layak di sumber untuk 34 merek (setelah filter nama dan wilayah): HBO Comedy, Showtime, MGM+, FXX, FX Movie Channel, Fox Movies, Fox Life, Freeform, ABC, CBS, The CW, Travel Channel, Science Channel, Toonami, DAZN, SuperSport, NBC Sports, MLB Network, Rugby TV, WWE, UFC, Motorsport TV, i24 News, ITV1, Film4, Dave, Sky Atlantic, Sat.1, TF1, Canal+, ARTE, Telecinco, VRT 1, SRF 1. TERBUKTI dari out/refill_scan.txt. Catatan: ABC, CBS, NBC, PBS di sumber hanya stasiun lokal (ABC KXXV dst), bukan network nasional, sengaja tidak dicocokkan. Showtime hanya Showtime Family Zone (sudah di folder Film).
- Aturan pilih: hanya status LOLOS tes lokal yang dinaikkan; belum dites atau gagal tidak pernah. Entri DRM dan entri berkredensial tidak pernah dipilih (113 entri terdeteksi berkredensial, sebagian mungkin salah deteksi, efeknya cuma tidak dipilih). Urutan wilayah: Asia, US, Latin America, UK, Eropa. Satu perubahan dari usulan sebelumnya (Asia, Latin America, US): US dinaikkan di atas Latin America karena berbahasa Inggris. Ubah di `region_order` kalau tidak setuju. Varian Latin America biasanya audio Spanyol atau Portugis (DUGAAN, belum dicek).
- Folder UK hanya menerima wilayah uk; folder Eropa hanya eu atau tanpa kode negara; folder lain tidak menerima varian Eropa berbahasa lokal.
- Tes di sandbox: alur penuh `bash refill.sh` jalan sampai selesai (build, scan, tes, pilih, build final); semua tes stream gagal karena sandbox tanpa jaringan, jadi 0 dinaikkan. Logika pilih dicoba dengan status acak palsu di folder sementara (bukan data asli, tidak ikut zip): 35 merek naik, hasil kedua kalinya sama (idempoten). Kualitas hasil nyata BELUM terbukti sampai dijalankan di Mac.
- Langkah Mac: `bash refill.sh` (WiFi rumah MyRepublic), baca `out/refill_laporan.txt`, upload `build.py`, `data/status_lokal.json`, `data/refill_pick.json` ke repo, refresh playlist di TiviMate. Merek yang kurang: tambah satu baris di `major_brands.yml` (n, a, f).

## Inventaris SELESAI (14 Nov malam, Mac)
- Fase 1 selesai. 14 baris v5 yang hilang sudah ditempel di bagian "Dipulihkan dari v5"; isinya era sandbox (sebelum refill jalan), jadi bagian "Hasil refill.sh" dan "STATUS TERBARU v4" menang jika bertentangan. Antrian Q10 = SELESAI di Mac (upload GitHub ditunda).
- ~/tv/iptv hanya berisi index.m3u (2.6M, 13 Nov), sisa lama, DUGAAN tidak dipakai.
- Zip iptv_kirim_1411_2020.zip basi (dibuat sebelum catatan inventaris). Zip pengganti: iptv_handoff_DDMM_HHMM.zip (dibuat manual). Jangan jalankan kirim.sh: rm -f menghapus iptv_kirim*.zip termasuk iptv_kirim_v5_PULIHAN.zip.
- FASE 2 (menunggu go user): ~/IPTV_BACKUP (zip/, trash-rescue/, snapshot/), docs/PETA_FILE.md, backup.sh, kirim.sh memindah bukan rm, SALIN item IPTV di Trash ke trash-rescue (bukan pindah), pindahkan iptv-upload dan update.yml.untuk-github ke arsip. FASE 3: tes restore dari snapshot (build di /tmp; angka acuan masuk=12530 playlist=11850 duplikat=680).
- Region_order [asia, us, uk, eu, other, latam] BELUM dijalankan, menunggu go terpisah.

## FASE 2 SELESAI (14 Nov malam, Mac) angka ditulis oleh skrip
- Dibuat: ~/IPTV_BACKUP/{zip,trash-rescue,snapshot,arsip-downloads}, backup.sh, kirim.sh baru (memindah zip lama ke IPTV_BACKUP/zip, bukan rm; memanggil backup.sh; membuat iptv_kirim_DDMM_HHMM.zip), docs/PETA_FILE.md. kirim.sh lama dibackup di _arsip/kirim.sh.sebelum-fase2.
- Trash: 11 item IPTV disalin (bukan dipindah) ke ~/IPTV_BACKUP/trash-rescue, venv dilewati. Isi Trash masih utuh.
- Dipindah dari Downloads ke IPTV_BACKUP/arsip-downloads: 2 item (iptv-upload, update.yml.untuk-github).
- Aturan baku ada di docs/PETA_FILE.md. Zip aktif satu saja, dibuat dengan bash ~/Downloads/iptv/kirim.sh (sekarang aman: tidak menghapus).
- Fase 3 (tes restore dari snapshot) BELUM. Region_order BELUM.

## STATUS TERBARU v5 (14 Nov malam) <- BACA INI DULU. Daftar BELUM yang lengkap ada di STATUS TERBARU v4.
SELESAI: refill.sh dijalankan di Mac dan diperiksa; inventaris Downloads; Fase 2 (struktur backup, peta file, kirim.sh aman).
BELUM (urut): go region_order; Fase 3 tes restore (build dari snapshot di /tmp, angka acuan masuk=12530 playlist=11850 duplikat=680); Q2 tes STB (adb offline); cek run terjadwal GitHub; Q3 ukur jadwal dhanytv 18-19 Nov; upload ke GitHub ditunda; entri HBO berkredensial; Fase B.
PESAN PEMBUKA v5 (tempel ke chat baru bersama zip iptv_kirim_*.zip dari ~/Downloads):
Lanjutkan proyek IPTV. Baca docs/handoff-iptv.md di zip, mulai dari bagian STATUS TERBARU v5 (paling ujung file), lalu STATUS TERBARU v4 dan docs/PETA_FILE.md, lalu 0. ATURAN KERJA, lalu README.md. Tanya konteks yang kurang sebelum mulai. Posisi: refill selesai di Mac, upload GitHub ditunda, backup dan peta file selesai, menunggu go untuk Fase 3 dan region_order. Aturan: gue/lo kasual, hemat token, Aksi lo di atas, satu blok perintah per pesan tanpa komentar, jelaskan tiap perintah, tandai TERBUKTI vs DUGAAN, kerja per fase dan jangan ubah file sebelum gue bilang go, handoff selalu siap pindah.

## STATUS TERBARU v6 (14 Nov malam, Mac) <- BACA INI DULU. Menggantikan v5 untuk posisi terakhir. Daftar BELUM v5 dan v4 tetap berlaku.
SELESAI (TERBUKTI dari output Mac):
- diff -rq proyek aktif vs snapshot terbaru di ~/IPTV_BACKUP/snapshot: tidak ada perbedaan. Tidak ada file aktif yang cuma ada di backup.
- Backup itu salinan: backup.sh pakai rsync (sumber utuh), kirim.sh cuma mv zip lama (iptv_kirim*.zip, iptv_handoff*.zip) ke ~/IPTV_BACKUP/zip. Isi zip/ sekarang: iptv_handoff_1411_2031.zip, iptv_kirim_v5_PULIHAN.zip, iptv_kirim_1411_2020.zip.
- PESAN_PEMBUKA.txt (v5, 688 byte) ditemukan di root ~/IPTV_BACKUP (dibuat manual 20:41, tidak ditulis skrip mana pun, tidak ada di peta). Disalin ke ~/Downloads/iptv/PESAN_PEMBUKA.txt (ikut zip dan snapshot), peta file diperbarui, salinan lama di backup dibiarkan. File ini sekarang berisi v6.
- Pesan pembuka lama di handoff (baris sekitar 73, 120, 262, 300, 428, 478) BASI. Hanya yang paling ujung file yang valid. Belum dirapikan.
CELAH DIKETAHUI (belum diperbaiki, menunggu go): kirim.sh memindah zip lama ke backup SEBELUM zip baru dibuat. Kalau pembuatan zip gagal, Downloads tidak punya zip aktif. Perbaikan yang diusulkan: pindahkan zip lama hanya setelah zip baru berhasil.
BELUM (urut): go region_order; Fase 3 tes restore (build dari snapshot di /tmp, angka acuan masuk=12530 playlist=11850 duplikat=680); perbaikan urutan kirim.sh; Q2 tes STB (adb offline); cek run terjadwal GitHub; Q3 ukur jadwal dhanytv 18-19 Nov; upload ke GitHub ditunda; entri HBO berkredensial; Fase B.
RUTIN: tiap ada perubahan berarti, tambah bagian status baru di ujung handoff, perbarui PESAN_PEMBUKA.txt, lalu bash ~/Downloads/iptv/kirim.sh.
PESAN PEMBUKA v6 (tempel ke chat baru bersama zip iptv_kirim_*.zip dari ~/Downloads):
Lanjutkan proyek IPTV. Baca docs/handoff-iptv.md di zip, mulai dari bagian STATUS TERBARU v6 (paling ujung file), lalu STATUS TERBARU v5, STATUS TERBARU v4 dan docs/PETA_FILE.md, lalu 0. ATURAN KERJA, lalu README.md. Tanya konteks yang kurang sebelum mulai. Posisi: refill selesai di Mac, upload GitHub ditunda, backup, peta file, dan PESAN_PEMBUKA.txt selesai, menunggu go untuk Fase 3 dan region_order. Aturan: gue/lo kasual, hemat token, Aksi lo di atas, satu blok perintah per pesan tanpa komentar, jelaskan tiap perintah, tandai TERBUKTI vs DUGAAN, kerja per fase dan jangan ubah file sebelum gue bilang go, handoff selalu siap pindah.

## STATUS TERBARU v7 (14 Nov malam, Mac) <- BACA INI DULU. Menggantikan v6 untuk posisi terakhir. Daftar BELUM v6, v5, v4 tetap berlaku kecuali yang dicoret di bawah.
SELESAI (TERBUKTI dari output Mac):
- FASE 3 LOLOS: snapshot terbaru (iptv_1411_2054) disalin ke /tmp/iptv_uji_JAM, build.py dijalankan di sana: masuk=12530 playlist=11850 duplikat=680 ditahan=0, sama dengan angka acuan. cmp out/playlist.m3u vs ~/Downloads/iptv/out/playlist.m3u: identik byte demi byte. Backup terbukti bisa dipakai restore.
- kirim.sh diperbaiki (backup lama: _arsip/kirim.sh.sebelum-urutan-fix): urutan baru = backup.sh, zip baru ke file sementara .iptv_kirim_baru.tmp, cek unzip -tq, BARU zip lama dipindah ke ~/IPTV_BACKUP/zip (mv -n), terakhir file sementara diganti nama jadi iptv_kirim_DDMM_HHMM.zip. Kalau backup atau zip gagal, zip lama tetap di Downloads. TERBUKTI di sandbox (HOME palsu, kasus sukses dan zip gagal). Run pertama di Mac = pembuatan zip yang memuat status ini; hasilnya DUGAAN sehat sampai outputnya dicek.
- Folder uji /tmp/iptv_uji_* sementara, hilang sendiri saat Mac restart.
BELUM (urut): go region_order (edit satu baris di major_brands.yml jadi [asia, us, uk, eu, other, latam], lalu bash refill.sh dari WiFi rumah, bandingkan varian latam di out/refill_laporan.txt); Q2 tes STB (adb offline); cek run terjadwal GitHub; Q3 ukur jadwal dhanytv 18-19 Nov; upload ke GitHub ditunda; entri HBO berkredensial; Fase B; opsional rapikan pesan pembuka lama di handoff (baris 73, 120, 262, 300, 428, 478, 489 basi).
PESAN PEMBUKA v7 (tempel ke chat baru bersama zip iptv_kirim_*.zip dari ~/Downloads):
Lanjutkan proyek IPTV. Baca docs/handoff-iptv.md di zip, mulai dari bagian STATUS TERBARU v7 (paling ujung file), lalu STATUS TERBARU v6, v5, v4 dan docs/PETA_FILE.md, lalu 0. ATURAN KERJA, lalu README.md. Tanya konteks yang kurang sebelum mulai. Posisi: refill selesai di Mac, upload GitHub ditunda, backup, peta file, PESAN_PEMBUKA.txt dan Fase 3 tes restore selesai (lolos), kirim.sh sudah diperbaiki urutannya, menunggu go untuk region_order. Aturan: gue/lo kasual, hemat token, Aksi lo di atas, satu blok perintah per pesan tanpa komentar, jelaskan tiap perintah, tandai TERBUKTI vs DUGAAN, kerja per fase dan jangan ubah file sebelum gue bilang go, handoff selalu siap pindah.

## STATUS TERBARU v8 (14 Nov malam, Mac) <- BACA INI DULU. Menggantikan v7 untuk posisi terakhir. Daftar BELUM v7, v6, v5, v4 tetap berlaku kecuali yang dicoret di bawah.
SELESAI (TERBUKTI dari output Mac):
- kirim.sh baru terbukti sehat di Mac (koreksi v7 yang masih menulis DUGAAN): snapshot iptv_1411_2059, zip lama iptv_kirim_1411_2054.zip dipindah ke backup (bukan dihapus), zip baru iptv_kirim_1411_2059.zip (749125 byte) di Downloads, satu zip aktif.
- region_order dijalankan: major_brands.yml baris 8 sekarang [asia, us, uk, eu, other, latam] (komentar di ujung baris masih versi lama, abaikan). bash refill.sh: 353 kandidat, 0 dites (semua sudah punya status), hasil: build masuk=12530 playlist=11850 duplikat=680 ditahan=0; 66 sudah ada, 46 dinaikkan, 30 tidak ada yang hidup, 34 tidak ada di sumber. Baris [latam] di refill_laporan.txt: 15 sebelum, 15 sesudah. Baris playlist berubah: 0.
- Penyebab TERBUKTI (direproduksi di sandbox dari data yang sama, angka sama dengan Mac): untuk 15 merek yang pilihannya varian latam, tidak ada satu pun varian non-latam yang lolos tes (varian US semuanya GAGAL). Urutan wilayah tidak berefek sekarang, otomatis berlaku kalau nanti ada varian non-latam yang lolos. Merek: A&E, AMC, Disney Junior, FX, HBO 2, HBO Family, Lifetime, National Geographic, TCM, TNT, TNT Sports, USA Network, Universal TV, Univision, VEVO. Audio kemungkinan Spanyol atau Portugis: DUGAAN, belum dicek di STB.
- Cadangan sebelum langkah ini: _arsip/sebelum-region/ (major_brands.yml, refill_pick.json, status_lokal.json, refill_laporan.txt, playlist.m3u).
OPSI BELUM DIPUTUSKAN: membuang varian latam sepenuhnya (merek itu jadi tidak ada yang hidup; ubah allowed_regions; butuh go). Saran: cek audio di STB dulu (Q2).
BELUM (urut): Q2 tes STB (adb offline, perlu IP:port Wireless debugging dari STB; tes putar, EPG, pin, audio varian latam); cek run terjadwal GitHub (git clone, data/last_run.txt berubah); Q3 ukur jadwal dhanytv 18-19 Nov (habis 20 Nov 02:00 UTC); putuskan nomor folder dan jadwal upload ke GitHub (build.py, data/status_lokal.json, data/refill_pick.json saja); entri HBO berkredensial; Fase B; opsional rapikan pesan pembuka lama di handoff.
PESAN PEMBUKA v8 (tempel ke chat baru bersama zip iptv_kirim_*.zip dari ~/Downloads):
Lanjutkan proyek IPTV. Baca docs/handoff-iptv.md di zip, mulai dari bagian STATUS TERBARU v8 (paling ujung file), lalu STATUS TERBARU v7, v6, v5, v4 dan docs/PETA_FILE.md, lalu 0. ATURAN KERJA, lalu README.md. Tanya konteks yang kurang sebelum mulai. Posisi: refill dan region_order selesai (region_order tidak berefek karena 15 merek latam tidak punya varian non-latam yang lolos), backup dan tes restore lolos, kirim.sh aman, upload GitHub ditunda, menunggu keputusan langkah berikutnya (Q2 tes STB, cek run terjadwal GitHub, atau Q3 dhanytv). Aturan: gue/lo kasual, hemat token, Aksi lo di atas, satu blok perintah per pesan tanpa komentar, jelaskan tiap perintah, tandai TERBUKTI vs DUGAAN, kerja per fase dan jangan ubah file sebelum gue bilang go, handoff selalu siap pindah.

## STATUS TERBARU v9 (14 Nov malam, Mac) <- BACA INI DULU. Menggantikan v8 untuk posisi terakhir.
KEBUTUHAN USER (baru, WAJIB dicatat):
1. Channel di Likely Dead (213 entri, termasuk beberapa channel Indonesia) dan channel mati di folder utama harus DITANDAI (mark/pin) lalu dicari link alternatifnya satu per satu untuk direvive. Sumber alternatif: app bawaan STB (via adb) atau m3u/link yang user cari sendiri.
2. Audio varian latam = SPANYOL (user mendengar di app IPTV Mac, TERBUKTI laporan user). 15 merek latam (A&E, AMC, Disney Junior, FX, HBO 2, HBO Family, Lifetime, National Geographic, TCM, TNT, TNT Sports, USA Network, Universal TV, Univision, VEVO) bahasanya salah untuk tujuan playlist. Membuang varian latam kembali jadi opsi nyata (ubah allowed_regions; butuh go).
3. User curiga ada channel di folder utama yang sebenarnya mati, makanya perlu penanda.
4. TARGET: minimal 90 persen channel folder utama (bukan Archive) benar-benar bisa nyala. Channel tanpa link alternatif: ditunda, tapi tetap ditandai.
BASELINE TERBUKTI (dihitung dari data zip yang sama dengan Mac, build identik): folder utama 01-15 = 394 entri. Selain Radio (folder 15, 108 entri, 100 belum dites): 286 entri, 279 lolos tes lokal, 7 gagal = 97.6 persen. Gagal per folder: 01 National TV 2, 02 News 1, 03 Islam 2, 04 Football 1, 08 Kids 1. Likely Dead = 213 entri. CATATAN: lolos tes lokal berarti HTTP terjangkau dari WiFi rumah, bukan bukti video jalan. Metrik 90 persen sekarang belum mengukur yang dirasakan user (DUGAAN: ada yang lolos tes tapi mati di player). Perlu tes lebih ketat (manifest dan segmen) dan laporan dari app atau STB.
GITHUB (TERBUKTI dari tab Actions): hanya 2 run, keduanya Manually run oleh styleb0yz (16:15 WIB 14m14s, 16:56 WIB 49s), sukses. TIDAK PERNAH ada run Scheduled, termasuk 19:30 WIB. Sebab DUGAAN: jadwal baru diedit 17:04 WIB, GitHub telat atau melewati. Run terjadwal berikutnya 03:30 WIB 15 Nov; cek tab Actions pagi hari. API anonim kena rate limit 403 dari IP user.
SERVER TES LOKAL: python http.server di Mac, port 8000, 127.0.0.1, melayani ~/Downloads/iptv/out/playlist.m3u (11850 channel TERBUKTI). URL http://localhost:8000/playlist.m3u. Mati: pkill -f "http.server 8000"; hilang kalau Mac restart. Tes di app IPTV Mac (nama app belum disebut): baru audio latam yang dilaporkan; folder, Indonesia nasional, SCTV, EPG belum dilaporkan.
RENCANA REVIVE (usulan, BELUM jalan, butuh go per fase):
R1 daftar mati: skrip baca data/status_lokal.json dan out/channels.json, tulis docs/revive_list.csv (nama, folder, negara, alasan gagal, ada kandidat alternatif di sumber atau tidak). Cakupan: 7 gagal folder utama, 213 Likely Dead, 15 latam. Tidak mengubah playlist.
R2 tes ulang: bash tes_lokal.sh semua dari WiFi rumah (cadangkan data/status_lokal.json dulu), plus 100 radio yang belum dites. Jangan jalan bersamaan dengan tes di app Mac.
R3 cari alternatif: (a) app bawaan STB via adb (pm list packages -3, ambil URL playlist app penjual; butuh STB, besok); (b) m3u atau link dari user ke data/extra/ atau extra_sources.txt; (c) sumber publik. Cek asal dan lisensi sebelum masuk playlist publik.
R4 penandaan: cara belum diputuskan (opsi: sufiks seperti [MATI] di nama, atau folder khusus Revive di atas Archive). Tes dampak di TiviMate dulu (butuh STB).
R5 ukur ulang metrik 90 persen dengan tes lebih ketat plus laporan user.
BELUM (urut): cek tab Actions pagi 15 Nov (run Scheduled 03:30 WIB); STB besok (adb: baca IP:port Wireless debugging, Q2, pm list packages -3, tes pin dan penandaan); R1 sampai R5; putuskan nasib 15 merek latam; lengkapi tes app Mac (folder, nasional, SCTV, EPG; catat NAMA channel yang gagal); Q3 dhanytv 18-19 Nov; upload GitHub ditunda; entri HBO berkredensial; Fase B; rapikan handoff (pesan pembuka dan status lama basi).
PESAN PEMBUKA v9 (tempel ke chat baru bersama zip iptv_kirim_*.zip dari ~/Downloads):
Lanjutkan proyek IPTV. Baca docs/handoff-iptv.md di zip, mulai dari bagian STATUS TERBARU v9 (paling ujung file), lalu STATUS TERBARU v8, v7, v6, v5, v4 dan docs/PETA_FILE.md, lalu 0. ATURAN KERJA, lalu README.md. Tanya konteks yang kurang sebelum mulai. Posisi: refill, region_order, backup, tes restore selesai; target baru user = minimal 90 persen channel folder utama benar-benar nyala, channel mati ditandai lalu direvive dengan cari link alternatif (rencana R1 sampai R5 di STATUS v9, menunggu go); audio varian latam = Spanyol; GitHub belum pernah menjalankan run terjadwal; STB baru bisa diakses besok. Aturan: gue/lo kasual, hemat token, Aksi lo di atas, satu blok perintah per pesan tanpa komentar, jelaskan tiap perintah, tandai TERBUKTI vs DUGAAN, kerja per fase dan jangan ubah file sebelum gue bilang go, handoff selalu siap pindah.

## STATUS TERBARU v10 (14 Nov malam, Mac) <- R1 jalan (user bilang go R1). Menggantikan v9 untuk posisi terakhir; v9 tetap berlaku untuk rencana R2-R5.
- TERBUKTI (sandbox, data zip yang sama): zip tidak memuat out/, jadi build ulang dulu (masuk=12530 playlist=11850, Likely Dead=213, cocok dengan Mac). Baseline folder utama tanpa radio 279/286 = 97.6%, 7 gagal: RRI Net, SCTV, BeritaSatu, Al-Iman TV, Surau TV, TVRI Sport, Mentari TV. Dari 7 itu, 6 tanpa alternatif di sumber, 1 punya alternatif belum dites.
- TERBUKTI (sandbox): Likely Dead 213 = 53 punya alt lolos, 44 alt belum dites, 116 tanpa alt; 21 di antaranya Indonesia. 15 varian latam: 6 punya alt lolos, 1 belum dites, 8 tanpa alt.
- R1 = revive_list.py (baca saja, tidak mengubah playlist) menulis docs/revive_list.csv. Hasil di Mac: DUGAAN sama dengan sandbox sampai outputnya dicek.

## STATUS TERBARU v11 (14 Nov malam, Mac) <- R1 selesai, R2 jalan (user bilang go R2). Menggantikan v10; v9 tetap berlaku untuk R3-R5.
- TERBUKTI (Mac, output R1 sama persis dengan sandbox): docs/revive_list.csv = 335 baris. 7 gagal folder utama: RRI Net, SCTV, BeritaSatu, Al-Iman TV, Surau TV, TVRI Sport, Mentari TV (hanya Al-Iman punya kandidat, versi Lebanon 240p belum dites). Likely Dead 213: 37 sudah punya pengganti lolos di folder utama, 116 tanpa alternatif (46 HTTP 403, 23 HTTP 404, 42 URLError); 32 gagal DNS, 38 timeout (DUGAAN: sebagian DNS gagal karena DNS ISP rumah, belum dites dari jaringan lain). 15 latam: semua alternatif juga latam (ada yang Portugis), 8 merek tanpa alternatif.
- KOREKSI v9: check_local.py SUDAH unduh segmen terakhir (>1 KB, cek 0x47, kunci AES). Jadi "lolos tes lokal" lebih kuat dari yang ditulis v9. Yang belum diuji: playlist live benar-benar maju atau beku, isi segmen bisa dibuka ffprobe, laju byte stream langsung/radio. DRM tetap tidak bisa dibuktikan.
- R2 = tes_ketat.py (baca saja, tidak mengubah playlist atau status_lokal.json), hasil docs/tes_ketat.csv, cakupan folder 01-15 (394). TERBUKTI di sandbox pada server palsu: live=HIDUP, playlist beku=BEKU, segmen 100 byte=MATI, html=MATI, 404=MATI, radio lancar=HIDUP, radio lambat=MATI. Hasil di Mac: belum ada.

## STATUS TERBARU v12 (14 Nov malam, Mac) <- hasil R2 masuk. Menggantikan v11 untuk posisi terakhir; v9 tetap berlaku untuk R3-R5.
- TERBUKTI (Mac, tes_ketat.py, 394 channel, ffprobe ada): verdict HIDUP 338, MATI 42, DRM 6, BEKU 5, MPD_TIDAK_DIUJI 3.
- TERBUKTI: folder utama tanpa radio 248/286 HIDUP = 86.7%; kalau DRM/MPD dihitung 257/286 = 89.9%; radio 90/108 = 83.3%. Target 90% = minimal 258/286, jadi kurang sekitar 10 (ketat) atau 1 (kalau DRM/MPD dihitung).
- TERBUKTI per folder (HIDUP/total): 01 9/18, 02 6/8, 03 14/16, 04 21/26, 05 14/15, 06 46/47, 07 25/30, 08 10/15, 09 36/37, 10 1/2, 11 10/15, 12 13/14, 13 13/13, 14 30/30, 15 90/108. Terburuk: folder 01 National TV.
- TERBUKTI: 38 non-HIDUP utama = 24 MATI (7 gagal lama + 17 yang dulu lolos tes lokal) + 5 BEKU (WION, RT India, Nickelodeon Asia, Rai 1, VOX) + 6 DRM (RCTI, ANTV, MNCTV, Trans TV, Trans7, Kids TV; manifest dan segmen sehat, lisensi tidak bisa dibuktikan) + 3 MPD (S4C, Antena 3, La Sexta).
- DUGAAN (belum diselidiki): sebagian dari 17 MATI baru itu palsu. GTV kena HTTP 429 (kena batas laju karena 8 worker), MDTV/CSI Miami timeout, HGTV Asia = DASH tanpa akhiran .mpd (salah deteksi di skrip), 3 channel gagal ffprobe (BN Channel, MUTV, VTV) alasan penuh belum dilihat, Eleven Sports 2/4 segmen 188 byte (satu paket TS), 404 pada Fox News/Fox Business/MS NOW/Golf/beIN USA (dulu lolos). BEKU mungkin palsu juga (jeda 4-12 detik bisa kurang).
- TERBUKTI (metadata ffprobe, bukan telinga): tag audio di HIDUP utama: eng 49(+2), spa 12, por 1, und 46, kosong 77.

## STATUS TERBARU v13 (14 Nov malam, Mac) <- R2b jalan (user bilang go). Menggantikan v12; v9 tetap berlaku untuk R3-R5.
- TERBUKTI (output Mac): 38 channel utama non-HIDUP di R2. Penyebab: HGTV Asia = DASH di URL .m3u8 (bug skrip); GTV kena HTTP 429 (8 worker terlalu banyak); lima channel satu host tvsen6.aynaott.com (beIN USA, Golf Channel, Fox News, Fox Business, MS NOW) 404 padahal tes lokal sebelumnya lolos; Disney Channel 403, La 2 403 Geoblock; 7 gagal sejak tes lama (RRI Net, Al-Iman, Surau, SCTV, TVRI Sport, BeritaSatu, Mentari TV); MDTV dan CSI Miami timeout; Eleven Sports 2 dan 4 segmen 188 byte; Mezzo Live 196 byte; BEKU 5 (WION, RT India, Nickelodeon Asia, Rai 1, VOX); DRM 6; MPD 3.
- DUGAAN: BN Channel, MUTV, VTV gagal ffprobe karena fMP4 butuh init segment (segmen jalan, playlist maju). BEKU bisa palsu (jeda cek lama cuma 4-12 detik). Trans TV, Trans7, Kids TV berstatus VOD (ada ENDLIST) padahal harusnya live. 2 radio ICY 200 OK salah dibaca sebagai MATI.
- TERBUKTI (tag ffprobe, bukan telinga): audio spa pada HBO 2, HBO Family, Universal TV, AMC, TCM, FX, Disney Jr., Univision, NatGeo (Latin America), por pada Lifetime Latin America Brazil; 5 merek latam lain (A&E, TNT, TNT Sports, USA Network, Vevo) tidak berstatus HIDUP atau tag-nya bukan spa/por. Tag spa juga ada di Telemundo East HD, Discovery World, BBC News South Asia (DUGAAN: label BBC salah).
- R2b = tes_ketat.py versi baru (backup lama: _arsip/tes_ketat.py.sebelum-r2b): deteksi DASH di URL non-.mpd, BOM, ICY lewat socket, init segment fMP4 sebelum ffprobe, backoff HTTP 429, jeda BEKU 20 detik, cuplikan isi respons aneh, mode --only-from (hanya tes ulang yang bukan HIDUP, tampilkan angka gabungan). TERBUKTI di sandbox pada server palsu. Hasil di Mac: belum ada.

## STATUS TERBARU v14 (14 Nov malam, Mac) <- hasil R2b masuk. Menggantikan v13 untuk posisi terakhir; v9 tetap berlaku untuk R3-R5.
- TERBUKTI (Mac, tes_ketat.py --only-from, 56 channel dites ulang): angka gabungan folder utama tanpa radio 262/286 HIDUP = 91.6% (95.1% kalau DRM/MPD dihitung). Target 90% (minimal 258) tercapai menurut ukuran tes ini. Radio 92/108 = 85.2%.
- TERBUKTI: 16 channel utama berubah ke HIDUP: MDTV, BN Channel, MUTV, Eleven Sports 2 dan 4, CSI Miami (AES), WION, RT India, VTV, Nickelodeon Asia, Disney Channel US, Rai 1, VOX, Mezzo Live (+ HGTV Asia jadi MPD). Jadi sebagian besar "mati" di R2 = bug tester atau gagal sesaat, bukan channel mati. Satu tes saja tidak stabil; perlu tes berulang di waktu beda (R5).
- TERBUKTI: sisa 24 non-HIDUP utama = 6 DRM (RCTI, ANTV, MNCTV, Trans TV, Trans7, Kids TV), 4 MPD (HGTV Asia, S4C, Antena 3, La Sexta), 14 mati/beku: SCTV, GTV, RRI Net, BeritaSatu, Al-Iman TV, Surau TV, TVRI Sport, Mentari TV, beIN Sports USA, Golf Channel, Fox News, Fox Business, MS NOW (BEKU), La 2.
- DUGAAN: GTV tetap HTTP 429 setelah backoff (host r-plus.sedotcw3.workers.dev, mungkin pembatas laju keras, bukan mati). SCTV dan TVRI Sport satu host 202.150.172.59 timeout (mungkin host itu mati atau diblok dari rumah). Lima channel US/aynaott 404 konsisten, mungkin layanan itu mati.
- Playlist belum diubah sama sekali sejak refill; R1/R2/R2b cuma mengukur dan membaca. Perbaikan nyata (R3: link pengganti, R4: penandaan) belum jalan, butuh go.

## STATUS TERBARU v16 (14 Nov malam, Mac) <- user konfirmasi target B. Menggantikan v15; v9 tetap berlaku untuk R4-R5.
- TARGET FINAL (dari user): minimal 90% dari channel BERMASALAH berhasil direvive (bukan 90% channel folder utama). User butuh daftar masalah tiap channel dan penyebabnya. Channel yang berhasil direvive dimasukkan ke FOLDER UTAMA (R4, mengubah playlist, wajib backup dan tunggu go).
- Kesalahan alur: v9 menulis target sebagai "90% channel folder utama nyala", Claude mengukur itu (91.6%) tanpa mengonfirmasi maksudnya. Angka itu tidak menjawab target B.
- R1/R2/R2b = fase ukur dan diagnosa. Hasil nyata: 16 channel yang tampak mati ternyata sehat (bug tester atau gagal sesaat), jadi tidak perlu dicari link. Belum ada channel yang direvive, playlist belum diubah.
- Penyebut target B (perkiraan sandbox): utama 24 + radio 16 + Likely Dead 213 = sekitar 253-255, 90% = sekitar 230. DUGAAN: tanpa link baru hanya sekitar 120 (TERCOVER + PROMOSI_ALT + TES_ALT + TES_ULANG + STB). TERBUKTI (data Likely Dead): 76 gagal 403/geoblok, 32 DNS, 38 timeout dari 213. DUGAAN: sebagian pulih kalau dites dari jaringan lain (STB/hotspot) tanpa link baru.
- R3a (revive_kerja.py, dengan kolom kategori_masalah) menulis docs/revive_kerja.csv. Hasil di Mac: belum ada.

## STATUS TERBARU v17 (14 Nov malam, Mac) <- hasil R3a masuk dan KOREKSI pencocokan alternatif. Menggantikan v16; v9 tetap berlaku untuk R4-R5.
- TERBUKTI (Mac): R3a menghasilkan docs/revive_kerja.csv (268 baris). Penyebab masalah Likely Dead 213: 76 diblok 403/geoblok, 39 link dihapus 404, 38 host tidak merespons, 32 domain mati (DNS), 20 koneksi ditolak/putus, 4 lainnya, 2 stream kosong, 2 request ditolak 400. Folder utama 24: 7 link dihapus 404, 6 DRM, 4 DASH, 2 timeout, 2 DNS, 1 geoblok, 1 beku, 1 rate limit 429. Radio 16: 8 balas HTML, 4 404, 2 stream kosong, 1 timeout, 1 koneksi putus.
- BUG DITEMUKAN (TERBUKTI dari data sandbox = data Mac): pencocokan alternatif di R1 dan R3a terlalu longgar. 100 dari 108 radio punya canon kosong, jadi semua radio dianggap "alternatif" satu sama lain. 73 dari 213 Likely Dead hanya punya "alternatif" lewat canon yang sama dengan nama beda (BBC News UK HD vs BBC News South Asia, DAZN 1 Germany vs Portugal, NBC vs afiliasi lokal). Akibatnya angka "bisa dibereskan tanpa link baru" (116) kebesaran. Perkiraan setelah diperketat (nama sama, atau canon sama + nama mirip, + negara sama): sekitar 60 dari 255, jauh di bawah 90% (angka Mac belum ada).
- KOREKSI DUGAAN v16: tes ulang dari jaringan lain (hotspot, STB) kemungkinan TIDAK memulihkan yang geoblok 403, karena semua jaringan itu IP Indonesia. Yang mungkin pulih hanya DNS dan timeout yang disebabkan ISP rumah.
- Target B (90% dari ~255 bermasalah) jauh dari terjangkau tanpa banyak link baru dari sumber baru. Playlist belum diubah.

## STATUS TERBARU v18 (14 Nov malam, Mac) <- R3a final (pencocokan sudah diperketat), R3b jalan. Menggantikan v17; v9 tetap berlaku untuk R4-R5.
- TERBUKTI (Mac, docs/revive_kerja.csv, 268 baris): penyebut target B = 253 (utama 24 + radio 16 + Likely Dead 213), 90% = 228. Aksi: CARI_LINK 185 (utama 13, radio 12, Likely Dead 160; Indonesia 11), SUDAH_TERCOVER 25, PROMOSI_ALT 17 (radio 1, Likely Dead 16), TES_ALT 15 (radio 3, Likely Dead 12), TES_ULANG_LAMBAT 1 (GTV), TUNGGU_STB 10, KEPUTUSAN_LATAM 15 (di luar penyebut).
- TERBUKTI: tanpa link baru maksimal 58 dari 253 (23%); dengan STB 68 (27%). Sisa 185 butuh link baru. Likely Dead CARI_LINK per negara: us 60, uk 34, es 7, de 6, id 5, sg 5, in 5, fr 5, nz 5, nl 3.
- Folder utama CARI_LINK (13): RRI Net, SCTV, BeritaSatu, Al-Iman TV, Surau TV, TVRI Sport, beIN Sports USA, Golf Channel US, Fox Business, Fox News, MS NOW (beku), Mentari TV, La 2 (403 geoblok).
- DUGAAN: PROMOSI_ALT untuk ANTV, GTV, RCTI HD, Kids TV (Likely Dead Indonesia) mengarah ke entri DRM di folder utama, jadi hasilnya bergantung tes di STB.
- Sumber link baru hanya lewat tiga jalur yang sudah diputuskan user: (a) app bawaan STB via adb, (b) link atau m3u dari user ke data/extra/ atau extra_sources.txt (masih kosong), (c) sumber publik dengan asal dan lisensi dicek dulu. Jangan jadikan sumber: URL yang memuat kredensial di path (contoh aflaxtv.xyz).
- R3b = tes_ketat.py --urls-file pada alternatif (data/r3b_alt_urls.txt), hasil docs/tes_alt.csv dan docs/revive_siap.csv. Hasil di Mac: belum ada.

## STATUS TERBARU v20 (14 Nov malam, Mac) <- scraper situs resmi disiapkan (user bilang go). Menggantikan v19; v9 tetap berlaku untuk R4-R5.
- KOREKSI v15/v19: arsip TIDAK semuanya belum dites. GitHub Actions sudah menguji 11.044 URL (7.900 OK) dari IP GitHub; hanya hasil Mac (status_lokal.json) yang baru 662 URL. build.py membaca status_lokal dan status_github, tapi folder Mac tidak punya status_github.json, jadi 213 Likely Dead = versi tes Mac saja. Versi GitHub bisa jauh lebih besar (DUGAAN: mayoritas geoblok dari IP Amerika). Belum dibandingkan (ambil lewat git clone, bukan raw).
- TERBUKTI (hasil pencarian web): TVRI punya live streaming resmi di tvri.go.id/live dan TVRI Klik; satu laporan menyebut TVRI Klik butuh daftar gratis. Domain resmi channel lain di data/situs_scrape.txt = DUGAAN sampai dites.
- Permintaan user: (1) scrape situs resmi pakai skrip: go. (2) NOMOR di depan nama folder harus hilang (rules.yml/build.py baris 230-246 membentuk f"{i:02d} · label"). Rencana R6: toggle folder_numbers di rules.yml dan buang nomor hanya di group-title output (urutan entri di file tetap), tes di sandbox, lalu tes urutan grup di TiviMate (DUGAAN: TiviMate mengikuti urutan playlist, belum dibuktikan). Butuh go sebelum mengubah.
- scrape_situs.py (baca saja): patuh robots.txt, 1 detik antar request ke host sama, maksimal 8 halaman dan 8 file JS per situs, ekstrak URL .m3u8/.mpd dari HTML, JS dan iframe, tes pakai tes_ketat (dengan dan tanpa Referer), tandai bertoken, kredensial, tanda DRM. Tidak menembus login atau DRM. Output docs/scrape_hasil.csv dan docs/scrape_siap.txt (siap ditempel ke data/links_user.txt, lalu cek_link_baru.py). Hasil di Mac: belum ada.
- Link bertoken atau butuh Referer bisa mati cepat atau tidak jalan di TiviMate tanpa header referrer; R4 harus menyimpan opsi referrer di entri.

## STATUS TERBARU v20 (14 Nov malam, Mac) <- scraper situs resmi disiapkan (user bilang go). Menggantikan v19; v9 tetap berlaku untuk R4-R5.
- KOREKSI v15/v19: arsip TIDAK semuanya belum dites. GitHub Actions sudah menguji 11.044 URL (7.900 OK) dari IP GitHub; hanya hasil Mac (status_lokal.json) yang baru 662 URL. build.py membaca status_lokal dan status_github, tapi folder Mac tidak punya status_github.json, jadi 213 Likely Dead = versi tes Mac saja. Versi GitHub bisa jauh lebih besar (DUGAAN: mayoritas geoblok dari IP Amerika). Belum dibandingkan (ambil lewat git clone, bukan raw).
- TERBUKTI (hasil pencarian web): TVRI punya live streaming resmi di tvri.go.id/live dan TVRI Klik; satu laporan menyebut TVRI Klik butuh daftar gratis. Domain resmi channel lain di data/situs_scrape.txt = DUGAAN sampai dites.
- Permintaan user: (1) scrape situs resmi pakai skrip: go. (2) NOMOR di depan nama folder harus hilang (rules.yml/build.py baris 230-246 membentuk f"{i:02d} · label"). Rencana R6: toggle folder_numbers di rules.yml dan buang nomor hanya di group-title output (urutan entri di file tetap), tes di sandbox, lalu tes urutan grup di TiviMate (DUGAAN: TiviMate mengikuti urutan playlist, belum dibuktikan). Butuh go sebelum mengubah.
- scrape_situs.py (baca saja): patuh robots.txt, 1 detik antar request ke host sama, maksimal 8 halaman dan 8 file JS per situs, ekstrak URL .m3u8/.mpd dari HTML, JS dan iframe, tes pakai tes_ketat (dengan dan tanpa Referer), tandai bertoken, kredensial, tanda DRM. Tidak menembus login atau DRM. Output docs/scrape_hasil.csv dan docs/scrape_siap.txt (siap ditempel ke data/links_user.txt, lalu cek_link_baru.py). Hasil di Mac: belum ada.
- Link bertoken atau butuh Referer bisa mati cepat atau tidak jalan di TiviMate tanpa header referrer; R4 harus menyimpan opsi referrer di entri.

## ATURAN WAJIB HANDOFF (permintaan user, 15 Nov; berlaku di semua chat berikutnya)
1. Folder ~/Downloads/iptv adalah MASTER. Handoff, log, dan pesan pembuka di sana harus selalu lengkap; memori Claude hanya cadangan.
2. Semua perubahan file lewat blok Terminal (heredoc) yang menulis langsung ke ~/Downloads/iptv. Claude tidak memberi file atau zip unduhan dari sandbox-nya.
3. Setiap balasan yang menghasilkan temuan atau keputusan: blok Terminal pertama menambah STATUS baru ke handoff dan 1 entri di docs/LOG_CHAT.md, SEBELUM blok kerja. Balasan tanpa perubahan menulis "Catatan handoff: tidak ada perubahan".
4. docs/LOG_CHAT.md: satu entri per chat (nomor, waktu WIB, dikerjakan, ditunda, file baru/hilang), ditandai TERBUKTI atau DUGAAN. Log tidak pernah dihapus.
5. Awal chat: CEK PAKET dulu dan laporkan sebelum kerja: (a) jam file terbaru di zip dalam WIB (zip menyimpan UTC; WIB = UTC+7), (b) versi pesan pembuka vs STATUS handoff, (c) file yang disebut handoff tapi tidak ada di zip.
6. EXIT CHAT: bila user bilang "exit" atau "pindah", atau chat sudah panjang (Claude menawarkan sendiri), Claude memberi SATU blok Terminal: tambah STATUS dan log, jalankan bash ~/Downloads/iptv/kirim.sh, lalu tampilkan PESAN PEMBUKA terbaru utuh untuk ditempel ke chat baru bersama zip dari kirim.sh. Jangan kompres folder manual (kirim.sh mengecualikan out/, venv/, _arsip/, DS_Store dan membuat backup).
7. Claude tidak bisa melihat Mac atau ~/Downloads; hanya zip yang diupload user. Zip yang diupload harus dibuat SESUDAH blok exit terakhir.

## STATUS TERBARU v21 (15 Nov pagi, Mac) <- hasil scrape masuk dan audit paket. Menggantikan v20 untuk posisi terakhir; v9 tetap berlaku untuk R4-R5.
- TERBUKTI (chat terakhir sebelum v21): jawaban terakhir berisi blok v20 + scrape_situs.py; blok dijalankan 15 Nov 09:23-09:26 WIB dan output scrape belum pernah dikirim ke chat itu. R6 (hapus nomor folder) masih menunggu go.
- TERBUKTI (docs/scrape_hasil.csv, dibuat 15 Nov 09:26 WIB): scrape_situs.py sudah jalan di Mac untuk 5 situs. Kandidat HIDUP 3: BeritaSatu 2 URL (tenbytecdn.com master.m3u8) dan Al-Iman TV 1 URL (live.aliman.id/live/livestream.m3u8); ketiganya h264 1920x1080 aac, tanpa Referer, tanpa token, dan ditandai cek-drm karena ada tanda DRM/lisensi di halaman. TVRI Sport dan SCTV: tidak ada URL m3u8/mpd di HTML/JS (DUGAAN: dimuat dinamis lewat API/JS). RRI Net: gagal URLError.
- BELUM: ketiga URL HIDUP belum dimasukkan ke data/links_user.txt dan belum lewat cek_link_baru.py; playlist belum berubah sejak refill; belum ada link baru yang masuk; upload GitHub tetap ditunda. Status "Hasil di Mac: belum ada" pada v20 sudah usang.
- TERBUKTI (isi iptv.zip 15 Nov, folder dikompres manual: memuat out/ dan _arsip/ yang dikecualikan kirim.sh): docs/cari_link.csv, data/links_user.txt, dan cek_link_baru.py disebut di v20 tetapi TIDAK ada di folder itu. DUGAAN kuat: blok yang membuatnya belum pernah dijalankan. Buat ulang file-file ini sebelum langkah link baru.
- TERBUKTI: bagian v20 di file ini tertulis dua kali (identik). Judul v20 berlabel "14 Nov malam" padahal file ditulis 15 Nov 09:23 WIB (DUGAAN: label tidak diperbarui).
- TERBUKTI: iptv_kirim_1411_2225.zip = snapshot v9 (14 Nov 22:25 WIB), usang; basis kerja = folder ~/Downloads/iptv saat ini (iptv.zip 15 Nov = v20).
- Antrian: (1) buat ulang tiga file yang hilang, (2) uji tiga URL HIDUP terhadap tanda DRM sebelum promosi, (3) R4 promosi yang terbukti HIDUP ke folder utama (backup dan go), (4) R6 hapus nomor folder, (5) STB via adb, (6) bandingkan status_github.json (git clone), (7) keputusan 15 merek latam.

## STATUS TERBARU v22 (15 Nov siang, Mac) <- tiga file hilang dibuat ulang lewat blok Terminal. Menggantikan v21 untuk posisi terakhir.
- TERBUKTI (output Mac): blok v21 sukses, LOG_CHAT.md 1126 B dan PESAN_PEMBUKA.txt 1332 B ditulis 15 Nov 11:31 WIB.
- docs/cari_link.csv: dibuat dari docs/revive_kerja.csv, hanya aksi CARI_LINK (185 baris). Kolom nama_bersih dipakai untuk mencocokkan nama di data/links_user.txt. Kolom link_baru_isi_di_links_user_txt dibiarkan kosong.
- data/links_user.txt: template. Format "Nama | URL | catatan". Flag dari docs/scrape_siap.txt (butuh-referer, bertoken, cek-drm) boleh ditempel apa adanya.
- cek_link_baru.py: tes tiap baris links_user.txt pakai tes_ketat, hasil ke docs/cek_link_baru.csv beserta folder target dari cari_link.csv. Flag butuh-referer memakai Referer https://HOST/ dari flag scrape:HOST (DUGAAN: scraper tadi memakai URL halaman penuh, bukan host).
- TERBUKTI (sandbox, salinan iptv.zip): alur skrip jalan dengan link palsu (hasil MATI). DUGAAN: belum dites dengan link asli di Mac.
- BELUM: links_user.txt masih kosong; tiga URL HIDUP hasil scrape belum ditempel; playlist tidak berubah.
- Antrian: (1) tempel docs/scrape_siap.txt ke data/links_user.txt lalu jalankan cek_link_baru.py (uji tiga URL cek-drm), (2) R4 promosi yang terbukti HIDUP ke folder utama (backup dan go), (3) R6 hapus nomor folder, (4) STB via adb, (5) bandingkan status_github.json (git clone), (6) keputusan 15 merek latam.

## STATUS TERBARU v23 (15 Nov siang, Mac) <- tiga file hilang terbukti ada; uji tiga URL scrape dijalankan. Menggantikan v22 untuk posisi terakhir.
- TERBUKTI (output Mac, 15 Nov 11:33 WIB): docs/cari_link.csv 185 baris (38049 B), data/links_user.txt (336 B, template), cek_link_baru.py (2327 B) sudah ada di folder.
- Langkah ini: docs/scrape_siap.txt ditempel ke data/links_user.txt, lalu python3 cek_link_baru.py menguji tiga URL (BeritaSatu 2, Al-Iman TV 1). Hasil ke docs/cek_link_baru.csv. Hasil di Mac: belum ada sampai outputnya dikirim.
- Antrian: (1) baca hasil cek_link_baru dan putuskan soal tanda cek-drm, (2) R4 promosi yang terbukti HIDUP ke folder utama (backup dan go), (3) R6 hapus nomor folder, (4) STB via adb, (5) bandingkan status_github.json (git clone), (6) keputusan 15 merek latam.

## STATUS TERBARU v25 (15 Nov siang, Mac) <- audit permintaan user dan guide pindah chat. Menggantikan v24 untuk posisi terakhir.
- TERBUKTI (output Mac): 3 dari 3 link scrape HIDUP, h264 1920x1080: BeritaSatu 2 URL dan Al-Iman TV 1 URL (docs/cek_link_baru.csv). DUGAAN: tanda cek-drm hanya kata DRM di halaman situs; belum dites di TiviMate atau STB. cari_link.csv (185 baris), links_user.txt, cek_link_baru.py ada di folder sejak 15 Nov 11:33 WIB.
- TERBUKTI (build.py): sumber tambahan masuk lewat data/extra/*.m3u dan tvg-id harus sama dengan id iptv-org. tvg-id: BeritaSatu.id@SD (folder 02), AlImanTV.id@SD (folder 03). Contoh format: data/extra/gist_ahmadarif.m3u (tvg-id tanpa @SD).
- R4 tahap 1 BELUM dimulai (menunggu go user): backup.sh, tulis data/extra/links_user.m3u (3 link), python3 build.py (mengubah out/playlist.m3u), cek BeritaSatu dan Al-Iman TV di folder utama, restore dari backup kalau gagal. Tahap 2: 19 channel docs/revive_siap.csv (17 Likely Dead, 2 radio).
- AUDIT permintaan user yang belum dikerjakan atau kelewat:
  1. Guide pindah chat/akun harus ada di SETIAP balasan; sebelumnya terlewat.
  2. Nomor folder harus hilang (R6): diminta dua kali, belum dikerjakan. DUGAAN: STB masih menampilkan nomor karena playlist GitHub versi lama.
  3. Upload ke GitHub ditunda sejak refill; perubahan lokal belum terlihat di STB.
  4. Target 90 persen dari 253 vs fokus yang terjangkau (sekitar 28 channel): ditanyakan, belum dijawab.
  5. Cek tab Actions GitHub (run Scheduled 03:30 WIB 15 Nov): belum diminta dicek.
  6. Q3 ukur jadwal dhanytv 18-19 Nov (jadwal habis 20 Nov 02:00 UTC): ada tenggat, belum dikerjakan.
  7. STB: adb butuh IP:port Wireless debugging; TiviMate dengan https://styleb0yz.github.io/iptv-playlist/playlist.m3u belum dicoba; 10 channel TUNGGU_STB.
  8. Scrape: TVRI Sport dan SCTV tanpa URL, RRI Net URLError; Surau TV dan Mentari TV belum masuk daftar (domain resmi belum diketahui).
  9. links_user.txt dan extra_sources.txt belum berisi link dari user; 185 channel CARI_LINK butuh link baru.
  10. Keputusan 15 merek latam (audio Spanyol) belum diputuskan.
  11. User minta Claude membaca dan mengatur ~/Downloads langsung: tidak bisa di chat; solusi sementara blok Terminal dan zip kirim.sh; alat yang bisa akses folder lokal belum dijawab tuntas.
- Antrian: (1) R4 tahap 1, (2) R4 tahap 2, (3) R6 hapus nomor folder, (4) cek Actions GitHub, (5) STB/adb dan TiviMate, (6) Q3 sebelum 19 Nov, (7) status_github.json via git clone, (8) keputusan latam, (9) upload GitHub.

## STATUS TERBARU v26 (15 Nov, awal chat v26) <- hasil cek paket. Menggantikan v25 untuk posisi terakhir; daftar AUDIT dan antrian v25 tetap berlaku.
- TERBUKTI (zip iptv_kirim_1511_1140.zip): file terbaru handoff, LOG_CHAT, PESAN_PEMBUKA bertanda 04:40 UTC = 11:40 WIB, cocok dengan nama zip.
- TERBUKTI: pesan pembuka v25 cocok dengan STATUS v25 di handoff.
- TERBUKTI: heading STATUS v24 tidak ada di handoff (v25 menyebut "menggantikan v24"); v15 dan v19 juga tidak ada; blok v20 tertulis dua kali. DUGAAN: v24 tidak pernah tertulis atau hilang.
- TERBUKTI: data/extra/links_user.m3u belum ada (wajar, R4 belum mulai). status_github.json, data/last_run.txt, fase_b.py, guides.json tidak ada di zip (DUGAAN: hanya di repo GitHub atau Mac). out/ memang dikecualikan kirim.sh, jadi playlist.m3u tidak terlihat dari zip.
- TERBUKTI: PETA_FILE.md bagian "Pesan pembuka" masih menyebut versi v5 (usang).
- TERBUKTI: docs/cek_link_baru.csv berisi 3 HIDUP (BeritaSatu 2 URL beda UUID, Al-Iman TV 1), h264 1920x1080 aac. Tanda cek-drm masih DUGAAN.
- R4 tahap 1 BELUM dimulai (menunggu go). Playlist belum berubah.

## STATUS TERBARU v27 (15 Nov, chat v26) <- user bilang GO R4 tahap 1; sedang jalan. Menggantikan v26 untuk posisi terakhir.
- TERBUKTI (output Mac 12:08 WIB): blok STATUS v26 sukses, handoff 106973 B.
- TERBUKTI (kode build.py di zip): extra/*.m3u diperlakukan seperti dhanytv; grup digabung lewat tvg-id; rank: lolos lokal > belum dites > gagal. URL lama BeritaSatu (bpmedialive, DNS gagal, fails 7) dan Al-Iman (tv.aliman.id, 404, fails 7) berstatus gagal; URL baru belum ada di status_lokal.json (= belum dites). DUGAAN: URL baru menang dan masuk folder 02 dan 03.
- TERBUKTI (backup.sh): mengecualikan /out, jadi out/ disalin manual ke _arsip/out_sebelum_R4_TS sebelum build.
- Langkah R4 tahap 1: backup.sh, salin out/, bangun data/extra/links_user.m3u dari data/links_user.txt (tvg-id BeritaSatu.id@SD dan AlImanTV.id@SD), python3 build.py, cek folder 02 dan 03, bandingkan sebelum/sesudah. Restore: salin out_sebelum_R4_TS balik ke out/, pindahkan links_user.m3u ke _arsip.
- Hasil di Mac: belum ada sampai output dikirim. Upload GitHub tetap ditunda, STB belum terpengaruh.

## STATUS TERBARU v28 (15 Nov, chat v26) <- R4 tahap 1 SELESAI di Mac (lokal). Menggantikan v27 dan v26 untuk posisi terakhir; daftar AUDIT dan antrian v25 tetap berlaku.
- TERBUKTI (output Mac, TS=1511_1212, 12:12 WIB): snapshot ~/IPTV_BACKUP/snapshot/iptv_1511_1212 (7.4M) dan _arsip/out_sebelum_R4_1511_1212 dibuat; data/extra/links_user.m3u ditulis (3 entri: BeritaSatu 2, Al-Iman TV 1); build.py sukses; total EXTINF 11850 jadi 11852.
- TERBUKTI: BeritaSatu (folder Indonesia · News) dan Al-Iman TV (Indonesia) (folder Islam · Indonesia & Haramain) sekarang entri baru dari extra; dua entri lama (URL mati) pindah ke Archive · Likely Dead (jumlah folder itu kini 215).
- TERBUKTI: entri baru TANPA tvg-logo dan TANPA http-referrer (extra m3u tidak memuat logo). Logo hilang dari dua channel itu.
- DUGAAN: BeritaSatu URL kedua tidak masuk playlist (build.py: dhanytv_loser=report, jadi dicatat sebagai duplikat di out/laporan.md). Dicek di blok berikutnya.
- Kesalahan Claude: komentar # berkurung di blok dipaste ke zsh interaktif, memicu 4 error (missing end of string, unknown file attribute). Hanya baris komentar yang gagal, semua perintah lain jalan. Blok berikutnya tanpa komentar berkurung. Status v27 (blok 1) belum terkonfirmasi tertulis; v28 ini memuat fakta yang sama.
- BELUM: URL baru belum dites di TiviMate atau STB; cek-drm masih DUGAAN; status_lokal.json belum berisi URL baru; upload GitHub ditunda (STB belum terpengaruh). Hasil R4 tahap 1: 2 channel hidup dari 253 bermasalah.
- Antrian: (1) R4 tahap 1b: tambah tvg-logo ke extra lalu build ulang, (2) R4 tahap 2 (19 channel revive_siap.csv), (3) R6 hapus nomor folder, (4) cek Actions GitHub, (5) STB/adb dan TiviMate, (6) Q3 sebelum 19 Nov, (7) status_github.json via git clone, (8) keputusan latam, (9) upload GitHub, (10) rapikan handoff (v24/v15/v19 hilang, v20 ganda).

## STATUS TERBARU v29 (15 Nov, chat v26) <- konfirmasi R4 tahap 1 dan temuan BeritaSatu. Menggantikan v28 untuk posisi terakhir.
- TERBUKTI (output Mac): STATUS v27 dan v28 tertulis di handoff; pembuka sudah v28. build.py membaca links_user.m3u (3 entri), playlist 11852, duplikat 681, mati 215, folder 02 isi 8, folder 03 isi 16.
- TERBUKTI (playlist): di folder Indonesia · News, BeritaSatu memakai URL KEDUA (90369cf5...). URL pertama (e6b57b20...) TIDAK ada di playlist. Al-Iman TV (Indonesia) memakai live.aliman.id/live/livestream.m3u8. Dua entri lama (bpmedialive dan tv.aliman.id) ada di Archive · Likely Dead.
- TERBUKTI (kode build.py): pemenang grup ditentukan S.rank; yang kalah dari sumber dhanytv/extra hanya dicatat sebagai duplikat (dhanytv_loser=report) dan laporan.md hanya memuat 40 duplikat pertama dari 681, jadi absennya BeritaSatu 1 di laporan tidak membuktikan apa-apa.
- DUGAAN: BeritaSatu URL pertama kalah sebagai duplikat. Belum jelas kenapa yang kedua menang (urutan seharusnya memihak yang pertama). Dicek lewat grep di out/, data/extra, refill_pick.json, status_lokal.json.
- TERBUKTI: entri baru tanpa tvg-logo. Rencana tahap 1b (menunggu go): tambah tvg-logo ke data/extra/links_user.m3u (logo lama BeritaSatu https://i.postimg.cc/6pycF7Vx/300px-IDTV.png, Al-Iman https://i.imgur.com/Qj1EFf1.png), build ulang.
- Koreksi: zsh interaktif tidak menganggap baris yang diawali # sebagai komentar (muncul "command not found: #" dan error glob). Blok Terminal berikutnya TANPA baris komentar.
- Antrian: (1) tahap 1b logo (menunggu go), (2) R4 tahap 2 (19 channel), (3) R6, (4) cek Actions, (5) STB/adb dan TiviMate, (6) Q3 sebelum 19 Nov, (7) status_github.json, (8) latam, (9) upload GitHub, (10) rapikan handoff.

## STATUS TERBARU v30 (15 Nov, chat v26) <- URL BeritaSatu yang menang ternyata stream BTV yang sudah ada. Menggantikan v29 untuk posisi terakhir.
- TERBUKTI (output Mac dan data/index.m3u): URL kedua BeritaSatu (90369cf5...) SAMA dengan URL entri iptv-org BTV.id@SD (BTV Indonesia). Di out/playlist.m3u URL itu muncul dua kali: baris 111 (BeritaSatu) dan baris 113 (BTV), keduanya folder 02. URL pertama (e6b57b20...) tidak ada di playlist; hanya di out/kandidat_cek.json dan data/extra.
- TERBUKTI (kode build.py): entri folder esensial tidak pernah dibuang walau URL sama; rank memilih lolos-tes-lokal dulu. DUGAAN kuat: URL 90369cf5 sudah ada di status_lokal.json lewat tes BTV (grep -c = 1 baris di salinan sandbox), jadi berstatus lolos dan mengalahkan URL pertama yang belum dites. Dicek di blok berikutnya.
- Dampak: BeritaSatu hidup lagi tapi stream-nya sama dengan BTV. Link yang benar-benar baru dari scrape: Al-Iman TV 1 dan BeritaSatu URL pertama (tersingkir). DUGAAN: BTV dan BeritaSatu satu stasiun (BeritaSatu TV rebrand BTV).
- Kesalahan Claude: pada blok v29 grep dipotong head -10 sehingga baris status_lokal.json tidak tampil; bukan tanda URL tidak ada di status.
- Rencana tahap 1b revisi (menunggu go): hapus entri BeritaSatu 2 dari data/extra/links_user.m3u supaya URL pertama menang, tambah tvg-logo (BeritaSatu https://i.postimg.cc/6pycF7Vx/300px-IDTV.png, Al-Iman https://i.imgur.com/Qj1EFf1.png), build ulang, bandingkan dengan out_sebelum_R4_1511_1212.
- Antrian: (1) tahap 1b revisi (menunggu go), (2) R4 tahap 2 (19 channel), (3) R6, (4) cek Actions, (5) STB/adb dan TiviMate, (6) Q3 sebelum 19 Nov, (7) status_github.json, (8) latam, (9) upload GitHub, (10) rapikan handoff.

## STATUS TERBARU v31 (15 Nov, chat v26) <- penyebab BeritaSatu = stream BTV terbukti. Menggantikan v30 untuk posisi terakhir.
- TERBUKTI (output Mac): sebelum R4, entri BTV.id@SD sudah memakai URL 90369cf5... (ada di out_sebelum_R4_1511_1212/playlist.m3u). status_lokal.json: 90369cf5 ok=True, 1080, dicek 2026-11-14 11:39 UTC. URL e6b57b20... tidak ada di status_lokal.json (belum pernah dites di sana; hanya lolos cek_link_baru.py).
- TERBUKTI (kode dan data): BeritaSatu URL kedua menang karena rank memilih yang lolos tes lokal (lewat tes BTV) dibanding yang belum dites. BeritaSatu dan BTV kini satu URL di folder 02.
- Tahap 1b revisi MASIH menunggu go (hapus BeritaSatu 2 dari data/extra/links_user.m3u, tambah tvg-logo, build ulang, bandingkan). Playlist tidak diubah oleh blok ini.
- Antrian tidak berubah dari v30.

## STATUS TERBARU v32 (15 Nov, chat v26) <- user GO "dua-duanya berurutan": tahap 1b revisi dulu (sedang jalan), lalu R4 tahap 2. Menggantikan v31 untuk posisi terakhir.
- Tahap 1b: backup (snapshot, out/ ke _arsip/out_sebelum_1b_TS, links_user.m3u ke _arsip), tulis ulang data/extra/links_user.m3u dari data/links_user.txt dengan melewati URL 90369cf5 (sudah dipakai BTV) dan menambah tvg-logo (BeritaSatu postimg, Al-Iman imgur), build.py, cek folder 02 dan 03, bandingkan sebelum/sesudah.
- DUGAAN: BeritaSatu URL pertama (e6b57b20) menang atas entri lama yang gagal (status 2) karena belum dites (status 1); total playlist tetap 11852. Hasil di Mac: belum ada sampai output dikirim.
- data/links_user.txt tidak diubah (sumber tetap 3 link). R4 tahap 2 (19 channel docs/revive_siap.csv) menunggu hasil 1b.

## STATUS TERBARU v33 (15 Nov, chat v26) <- 1b SELESAI; R4 tahap 2 jalan (go user). Menggantikan v32 untuk posisi terakhir.
- TERBUKTI (output Mac, TS 1511_1229): tahap 1b sukses. Total 11852 (tetap), BeritaSatu folder 02 pakai e6b57b20 dengan logo, Al-Iman folder 03 pakai live.aliman.id dengan logo, 90369cf5 tinggal satu (BTV). Selisih sebelum/sesudah hanya dua baris (logo).
- Tahap 2 (revive_siap.csv, 19 baris, 15 URL alternatif unik; semua HIDUP di tes_alt.csv): DIPROMOSIKAN 5 URL lewat data/refill_pick.json (mekanisme refill build.py, entri arsip naik ke folder utama): Documentary+ dan Terra Mater WILD ke docs, Rakuten Viki dan Cinemax Asia Taiwan ke movies, MTV India ke music. Menutup 6 baris bermasalah (Documentary+ International, Terra Mater WILD English, Rakuten Viki, Cinemax Asia 720p dan HD, MTV India HD).
- TIDAK dipromosikan: (a) HBO (United States) dan HBO Hits (2 baris): URL aflaxtv.xyz memuat kredensial di path, aturan v18 melarang; (b) 9 baris varian Latin America (AXN, Cartoon Network, Disney Channel, E! x2, ESPN2 x2, ESPN x2): audio Spanyol (TERBUKTI laporan user), menunggu keputusan latam; (c) CNN Indonesia (radio) dan Suara Muslim Surabaya: alternatif sudah ada di folder utama (02 dan 15), tidak perlu pick (DUGAAN sampai playlist dicek).
- DUGAAN: sumber Cinemax (IP Taiwan, play.ts) dan MTV India (workers.dev) setara risiko lisensi dengan pick refill yang sudah ada (HBO Asia Taiwan, host sama). Belum dites di TiviMate atau STB.
- Backup: snapshot backup.sh, out/ ke _arsip/out_sebelum_t2_TS, refill_pick.json ke _arsip. Restore: salin balik out/ dan refill_pick.json dari _arsip.
- Hasil di Mac: belum ada sampai output dikirim. Upload GitHub tetap ditunda.
- Antrian: (1) cek hasil tahap 2, (2) keputusan latam (9 baris + 15 merek), (3) R6 hapus nomor folder, (4) cek Actions, (5) STB/adb dan TiviMate, (6) Q3 sebelum 19 Nov, (7) status_github.json, (8) upload GitHub, (9) rapikan handoff.

## STATUS TERBARU v34 (15 Nov, chat v26) <- tahap 2 SELESAI; temuan URL berkredensial di playlist. Menggantikan v33 untuk posisi terakhir.
- TERBUKTI (output Mac, TS 1511_1232): tahap 2 sukses. 51 dari 51 pick masuk; total 11852; folder 06 Movies 49, 12 Music 15, 13 Docs 15; selisih 10 baris (5 keluar dari Archive, 5 masuk folder utama): Cinemax Asia Taiwan, Rakuten Viki, MTV India, Documentary+, Terra Mater WILD. MTV India masuk dengan http-referrer https://bhoomtv.org/ (DUGAAN: feed pihak ketiga; belum dites di TiviMate).
- TERBUKTI: out/playlist.m3u memuat 5 baris URL aflaxtv.xyz (kredensial di path), semua di Archive · Others: HBO, HBO Hits, HBO Family, Cinemax, dan 1 lagi belum teridentifikasi. TERBUKTI (data/dhanytv.m3u di zip): 7 URL aflaxtv (HBO, HBO Hits, HBO Family, HBO Signature, Cinemax, Warner TV Asia, Indonesia Movie Channel Vision+). rules.yml hold masih kosong.
- TERBUKTI (update.yml): out/playlist.m3u di-deploy ke GitHub Pages publik. DUGAAN: playlist publik hasil Actions memuat URL itu selama sumber dhanytv memuatnya; dicek lewat curl hitung aflaxtv di Pages.
- Rencana R4c (menunggu go): tahan entri berkredensial lewat rules.yml hold (kanon 401, 402, 403, 405, dan lain setelah identifikasi) atau filter host di build.py; build ulang; cek hitungan aflaxtv = 0 sebelum upload GitHub. Upload GitHub tetap ditunda.
- Hitung jujur: channel bermasalah yang tertutup sekitar 10 dari 253 (4 persen); sisa 185 CARI_LINK butuh link baru dari user atau STB.
- Antrian: (1) R4c tahan kredensial, (2) keputusan latam (9 baris + 15 merek), (3) R6 hapus nomor folder, (4) cek Actions, (5) STB/adb dan TiviMate, (6) Q3 sebelum 19 Nov, (7) status_github.json, (8) upload GitHub, (9) rapikan handoff.

## STATUS TERBARU v36 (15 Nov, chat v26) <- keputusan user: aflaxtv dilolosin, R4c DIBATALKAN. Menggantikan v35 untuk posisi terakhir.
- KEPUTUSAN USER (15 Nov): entri aflaxtv.xyz (HBO, HBO Hits, HBO Family, Cinemax, Indonesia Movie Channel Vision+) dilolosin; user menganggap kredensial aman (pendapat user, tidak diverifikasi Claude). R4c (hold di rules.yml) dibatalkan, penjaga kredensial tidak dibuat. Aturan v18 "jangan jadikan sumber URL berkredensial" dicabut oleh user untuk aflaxtv.
- TERBUKTI: playlist publik GitHub Pages sudah memuat 5 baris aflaxtv sebelum sesi ini; playlist lokal juga 5.
- DUGAAN: akun reseller bisa dicabut kapan saja, entri aflaxtv bisa mati mendadak; jangan dihitung revive stabil.
- Blok pembatalan: bila rules.yml sudah berisi hold R4c (kanon "401"), dipulihkan dari _arsip/rules.yml.*.bak terbaru lalu build ulang; hasil di output Mac.
- Pertanyaan terbuka: HBO (United States) dan HBO Hits (revive_siap.csv, TES_ALT HIDUP, alternatif aflaxtv) dipromosikan ke folder utama movies lewat refill_pick.json? Menunggu jawaban user.
- Antrian: (1) jawaban promosi HBO dan HBO Hits, (2) upload GitHub (menunggu go), (3) keputusan latam, (4) R6 hapus nomor folder, (5) cek Actions, (6) STB/adb dan TiviMate, (7) Q3 sebelum 19 Nov, (8) status_github.json, (9) rapikan handoff.

## STATUS TERBARU v37 (15 Nov, 12:37 WIB, EXIT chat v26) <- posisi akhir sebelum pindah chat. Menggantikan v36 untuk posisi terakhir; daftar AUDIT di v25 tetap berlaku.
- TERBUKTI (output Mac, TS 1511_1237): blok v36 jalan. rules.yml hold masih `hold: []` (R4c tidak pernah terpasang), playlist 11852, aflaxtv 5, tidak ada perubahan. STATUS v35 TIDAK ADA di handoff (blok R4c v35 tidak pernah dijalankan; R4c dibatalkan user). PESAN_PEMBUKA.txt macet di v34 karena itu; ditulis ulang utuh sebagai v37.
- TERBUKTI (playlist lokal 11852, di Mac saja; GitHub dan STB belum tersentuh): R4 tahap 1, 1b, dan 2 SELESAI. BeritaSatu (folder 02) memakai URL e6b57b20 dan Al-Iman TV (folder 03) memakai live.aliman.id, keduanya dengan tvg-logo (data/extra/links_user.m3u). Lima pick tahap 2 lewat data/refill_pick.json (51 pick total): Documentary+ dan Terra Mater WILD ke folder 13; Rakuten Viki dan Cinemax Asia Taiwan ke folder 06; MTV India ke folder 12 (membawa http-referrer bhoomtv.org, DUGAAN belum dites di TiviMate).
- KEPUTUSAN USER: aflaxtv dilolosin (kredensial dianggap aman); R4c dibatalkan. TERBUKTI: playlist publik GitHub Pages sudah memuat 5 baris aflaxtv. DUGAAN: akun reseller bisa dicabut, entri aflaxtv tidak stabil.
- INSTRUKSI BARU USER (belum dikerjakan, perlu dikonfirmasi): "semua yang direvive, lebih baik cari pasangan di folder utama kalau memang major" (bukan hanya HBO). DUGAAN artinya: untuk tiap channel hasil revive berstatus merek mayor, cocokkan dengan entri sejenis yang sudah ada di folder utama dan tempatkan berpasangan (mis. HBO dengan HBO Asia Taiwan), bukan promosi lepas. Tanyakan arti pastinya sebelum mengubah. Pertanyaan terbuka terkait: HBO (United States) dan HBO Hits (alternatif aflaxtv, HIDUP di R3b) dipromosikan ke folder 06 atau tidak.
- Hitung jujur: channel bermasalah yang tertutup sekitar 10 dari 253 (4 persen); 185 CARI_LINK butuh link baru dari user atau app STB. 9 baris varian Latin America (audio Spanyol) belum dipromosikan, menunggu keputusan latam.
- Backup tahap ini: snapshot ~/IPTV_BACKUP/snapshot (1511_1212, 1511_1229, 1511_1232), _arsip/out_sebelum_R4_1511_1212, _arsip/out_sebelum_1b_1511_1229, _arsip/out_sebelum_t2_1511_1232, refill_pick.json dan rules.yml di _arsip.
- Catatan zsh: zsh interaktif tidak menganggap baris # sebagai komentar; blok Terminal tanpa baris komentar. Jangan pakai head -N pada grep yang perlu dibaca utuh.
- Antrian: (1) arti instruksi "pasangan di folder utama kalau major" dan promosi HBO, (2) upload GitHub (Pages publik masih versi lama; perlu go, daftar file disusun dulu), (3) keputusan latam (9 baris + 15 merek), (4) R6 hapus nomor folder, (5) cek tab Actions GitHub, (6) STB/adb dan TiviMate (tes BeritaSatu, Al-Iman, MTV India), (7) Q3 dhanytv sebelum 19 Nov (jadwal habis 20 Nov 02:00 UTC), (8) status_github.json via git clone, (9) rapikan handoff (v24, v19, v15, v35 tidak ada; v20 ganda; PETA_FILE masih sebut pembuka v5).

## STATUS TERBARU v38 (15 Nov, awal chat v27, setelah 12:44 WIB) <- hasil cek paket. Menggantikan v37 untuk posisi terakhir; daftar AUDIT v25 dan antrian v37 tetap berlaku.
- TERBUKTI (zip iptv_kirim_1511_1239.zip, diupload 12:44 WIB): file terbaru handoff, LOG_CHAT, PESAN_PEMBUKA bertanda 05:39 UTC = 12:39 WIB, cocok dengan nama zip. Pesan pembuka v37 cocok dengan STATUS v37.
- TERBUKTI (isi zip): rules.yml baris 52 `hold: []`; data/refill_pick.json 51 entri; data/extra/links_user.m3u 2 entri (BeritaSatu dan Al-Iman TV, dengan tvg-logo) sesuai v33; data/dhanytv.m3u memuat 7 baris aflaxtv.
- TERBUKTI: tidak ada di zip: out/ (dikecualikan kirim.sh), docs/status_github.json, data/last_run.txt, fase_b.py, guides.json. Karena out/ tidak ikut, angka playlist 11852 dan 5 aflaxtv di playlist hanya DUGAAN mengikuti v37, belum bisa diverifikasi dari zip.
- TERBUKTI: heading v35, v24, v19, v15 tidak ada (sesuai pembuka); v20 tertulis ganda; PETA_FILE.md bagian pembuka masih menyebut v5; LOG_CHAT tidak punya entri "lanjutan 9" (cocok dengan v35 yang tidak ada).
- Playlist dan file kerja tidak diubah chat ini. Pertanyaan pertama chat v27: arti pasti "pasangan di folder utama kalau major" (menunggu jawaban user).
- Antrian: sama dengan v37.

## STATUS TERBARU v39 (15 Nov, chat v27) <- keputusan arti "pasangan major". Menggantikan v38 untuk posisi terakhir; daftar AUDIT v25 dan antrian v37 tetap berlaku.
- KEPUTUSAN USER (15 Nov): "cari pasangan di folder utama kalau major" = opsi A: hasil revive merek mayor ditaruh di folder utama berdekatan dengan channel sejenis yang sudah ada (mis. HBO di dekat HBO Asia Taiwan). Entri tetap terpisah; bukan digabung jadi satu channel (opsi B), bukan sekadar promosi (opsi C).
- TERBUKTI (kode build.py): urutan dalam folder = (folder, pos, nama); pos default 10**6 + order. data/refill_pick.json punya field pos (HBO Asia Taiwan pos 0 di movies, Rakuten Viki 310, Documentary+ 610, Terra Mater WILD 620, MTV India 1750). DUGAAN: "berdekatan" dikerjakan dengan mengubah pos di refill_pick.json; belum dites.
- TERBUKTI: major_brands.yml memuat 176 merek (nama n, alias a, folder f). Definisi "mayor" = daftar ini, kecuali user mengganti.
- Langkah ini (baca-saja, python lewat heredoc, tanpa file baru): daftar hasil revive di folder utama (BeritaSatu, Al-Iman, Documentary+, Terra Mater WILD, Rakuten Viki, Cinemax Asia Taiwan, MTV India) dan 5 baris aflaxtv: status mayor, sefamili di folder yang sama dan folder utama lain, tetangga sekarang. Skrip dites di sandbox hanya dengan playlist palsu (DUGAAN: cocok dengan out/playlist.m3u asli). Hasil di Mac: belum ada.
- Antrian: (1) baca hasil, susun rencana pos (butuh go), (2) HBO dan HBO Hits ikut hasil itu, (3) upload GitHub (menunggu go), (4) latam, (5) R6, (6) cek Actions, (7) STB/adb dan TiviMate, (8) Q3 sebelum 19 Nov, (9) status_github.json, (10) rapikan handoff.

## STATUS TERBARU v40 (15 Nov, chat v27) <- bug skrip pasangan dan 5 aflaxtv teridentifikasi. Menggantikan v39 untuk posisi terakhir.
- TERBUKTI (output Mac): skrip baca-saja v39 jalan tanpa error: brands 176, entri playlist 11852, baris aflaxtv 5. Hasil "revive di folder utama: 0" = BUG skrip (Claude): skrip mengira group-title berawalan nomor "01 ·"; TERBUKTI group-title di out/playlist.m3u TANPA nomor (contoh "Archive · Others"). Daftar pasangan belum ada; skrip diperbaiki (folder utama = group yang tidak berawalan "Archive") dan diulang.
- TERBUKTI: 5 baris aflaxtv teridentifikasi, semua di Archive: Indonesia Movie Channel (Vision+) di Archive · Indonesia Local TV (138 dari 200); HBO (56), HBO Hits (57), HBO Family (58), Cinemax (59) di Archive · Others (115 entri). HBO, HBO Hits, HBO Family, Cinemax masing-masing punya kembaran "(IHT)" di Archive · Others (urutan 106 sampai 110).
- DUGAAN: karena group-title lokal sudah tanpa nomor, R6 (hapus nomor folder) mungkin sudah efektif di out/playlist.m3u lokal; belum dicek rules.yml/build.py dan playlist GitHub (versi lama).
- Hasil di Mac untuk skrip yang diperbaiki: belum ada. Antrian sama dengan v39.

## STATUS TERBARU v42 (15 Nov, chat v27) <- keputusan lingkup R4d. Menggantikan v41 untuk posisi terakhir.
- KEPUTUSAN USER (15 Nov): lingkup R4d = reposisi 2 saja (Cinemax Asia Taiwan dan MTV India). HBO (United States) dan HBO Hits (aflaxtv) TIDAK dipromosikan; tetap di Archive · Others. Ini menjawab pertanyaan terbuka v36/v37 (HBO dan HBO Hits: tidak).
- Rencana R4d (menunggu go user): backup.sh, out/ ke _arsip/out_sebelum_r4d_TS, refill_pick.json ke _arsip; ubah pos di data/refill_pick.json: Cinemax Asia Taiwan 300 jadi -499922.5 (kunci 77.5, tepat setelah Cinemax Classics baris draft 77), MTV India 1750 jadi -499682.5 (kunci 317.5, tepat setelah MTV Spankin' New baris draft 317); python3 build.py; cek urutan di Movies and Series dan Music; bandingkan sebelum/sesudah (harus selisih hanya urutan dua entri, total tetap 11852). Restore: salin balik out/ dan refill_pick.json dari _arsip.
- TERBUKTI (kode refill.py baris 247): refill.py menulis ulang data/refill_pick.json. DUGAAN: menjalankan refill.sh lagi bisa mengembalikan pos ke nilai lama (baris 173 membaca pick_old, belum dicek apakah pos manual dipertahankan). Jangan jalankan refill.sh sesudah R4d tanpa mengecek.
- Hasil di Mac: belum ada (R4d belum jalan). Antrian sama dengan v41, tanpa butir HBO.

## STATUS TERBARU v43 (15 Nov, chat v27) <- user GO R4d; sedang jalan. Menggantikan v42 untuk posisi terakhir.
- KEPUTUSAN USER (15 Nov): go R4d, lingkup reposisi 2 (Cinemax Asia Taiwan dan MTV India).
- Langkah (blok TS di LOG_CHAT): backup.sh; out/ ke _arsip/out_sebelum_r4d_TS; refill_pick.json ke _arsip/refill_pick.json.sebelum_r4d_TS; pos Cinemax Asia Taiwan 300 jadi -499922.5, MTV India 1750 jadi -499682.5; python3 build.py (argumen sama dengan tes_lokal.sh); bandingkan sebelum/sesudah. Restore: salin balik out/ dan refill_pick.json dari _arsip.
- Hasil di Mac: belum ada sampai output dikirim. Upload GitHub tetap ditunda. Jangan jalankan refill.sh sesudah R4d tanpa mengecek (DUGAAN: menimpa pos).

## STATUS TERBARU v44 (15 Nov, 13:04 WIB, chat v27) <- R4d SELESAI di Mac (lokal). Menggantikan v43 untuk posisi terakhir; daftar AUDIT v25 berlaku.
- TERBUKTI (output Mac, TS 1511_1304): backup ada (snapshot iptv_1511_1304 36M, _arsip/out_sebelum_r4d_1511_1304, _arsip/refill_pick.json.sebelum_r4d_1511_1304). pos Cinemax Asia Taiwan 300 jadi -499922.5, MTV India 1750 jadi -499682.5. build.py jalan tanpa error dengan pos pecahan negatif (DUGAAN v41 terbukti).
- TERBUKTI (verifikasi sebelum/sesudah): total 11852 sama; isi sama (abaikan urutan) = True; urutan hanya berubah di dua folder: Movies and Series dan Music. Movies and Series: [3] Cinemax Hits, [4] Cinemax Classics, [5] Cinemax Asia Taiwan, [6] Charge!. Music: [2] MTV Biggest Pop, [3] MTV Spankin' New, [4] MTV India, [5] Mezzo Live.
- TERBUKTI: R4d hanya mengubah urutan; tidak menambah channel bermasalah yang tertutup (hitung jujur tetap sekitar 10 dari 253). HBO (United States) dan HBO Hits tetap di Archive (keputusan user).
- TERBUKTI (output Mac): group-title di out/playlist.m3u lokal TANPA nomor folder; ringkasan build di terminal masih memakai nomor (47 sampai 71 · Archive). DUGAAN: R6 sudah efektif di playlist lokal; kode yang membuang nomor belum dibaca; Pages publik (versi lama) belum dicek.
- Belum di GitHub dan STB: semua perubahan R4, R4d masih lokal.
- Antrian: (1) upload GitHub (menunggu go; susun daftar file dulu), (2) STB/adb dan TiviMate (tes BeritaSatu, Al-Iman, MTV India, Cinemax Asia Taiwan), (3) keputusan latam (9 baris + 15 merek), (4) cek R6 di Pages publik, (5) cek tab Actions, (6) Q3 dhanytv sebelum 19 Nov, (7) status_github.json, (8) rapikan handoff.

## STATUS TERBARU v45 (15 Nov, chat v27) <- keputusan latam dan aturan baru. Menggantikan v44 untuk posisi terakhir.
- TERBUKTI (output Mac): STATUS v44 dan log tertulis (grep = 1). STATUS v45 versi "fakta latam" dari balasan sebelumnya TIDAK pernah dijalankan; isinya digabung di sini.
- KEPUTUSAN USER (15 Nov): latam = opsi A. 15 varian Latin America yang sudah di folder utama TETAP di sana (HBO 2, HBO Family, Universal TV, AMC, TCM, FX, Lifetime Brazil di Movies and Series; TNT, USA Network, A&E Brazil, Univision di America; National Geographic di Docs; Disney Jr. di Kids; TNT Sports Argentina di Sports; Vevo Latino di Music). TERBUKTI (tag ffprobe): 9 bertag spa, 1 por, 1 eng, sisanya kosong, und, atau tanpa data. 9 baris latam di revive_siap (AXN, Cartoon Network, Disney Channel, E! x2, ESPN2 x2, ESPN x2) tetap TIDAK dipromosikan. Antrian "keputusan latam" SELESAI.
- ATURAN BARU USER (15 Nov): jangan kirim survey atau tombol pilihan (ask_user_input_v0) terus-menerus. Tanya lewat teks, satu pertanyaan, hanya bila perlu; kalau ada langkah berikutnya yang jelas, jalankan saja dan sebut asumsinya.
- Langkah ini (baca-saja, tulis hanya ke /tmp): git clone styleb0yz/iptv-playlist ke /tmp/iptv_repo, bandingkan dengan folder lokal (tanpa venv, out, _arsip, docs, file milik workflow) untuk menyusun daftar file upload GitHub; lihat isi data/ repo (status_github.json, last_run.txt). Hasil di Mac: belum ada.
- Antrian: (1) daftar upload GitHub dari hasil diff (lalu go upload), (2) STB/adb dan TiviMate, (3) cek R6 di Pages publik, (4) cek tab Actions, (5) Q3 dhanytv sebelum 19 Nov, (6) status_github.json (dari clone), (7) rapikan handoff.

## STATUS TERBARU v46 (15 Nov, sekitar 13:19 WIB, chat v27) <- daftar upload GitHub. Menggantikan v45 untuk posisi terakhir.
- TERBUKTI (output Mac): STATUS v45 dan log tertulis (grep = 1). Blok python pembuka mencetak False karena cek huruf kecil vs besar (bug Claude); penyisipan kalimat "Jangan kirim survey..." diverifikasi dengan grep di blok ini. Jangan jalankan ulang blok python itu (bisa dobel).
- TERBUKTI (git clone repo styleb0yz/iptv-playlist): commit terakhir d5b7374 15 Nov 00:04:58 UTC (07:04 WIB) "data 2026-11-15". data/ repo memuat status_github.json (2217033 B) dan last_run.txt. DUGAAN: itu run terjadwal 03:30 WIB yang telat; run 11:30 WIB belum terlihat di clone (telat, tanpa perubahan data, atau gagal). Cek tab Actions.
- TERBUKTI (diff -rq): file lokal yang beda dari repo dan relevan: build.py, data/status_lokal.json (repo 89071 B, lokal 134120 B), data/refill_pick.json (baru), data/extra/links_user.m3u (baru). Selebihnya hanya alat dan data kerja Mac (backup.sh, cek_link_baru.py, refill.py, refill.sh, revive_*.py, scrape_situs.py, tes_ketat.py, major_brands.yml, links_user.txt, r3b_alt_urls.txt, situs_scrape.txt, update.yml) dan file beda yang tidak perlu diunggah (kirim.sh, epg_check.py). rules.yml dan draft_esensial.csv identik dengan repo.
- TERBUKTI (update.yml dan kode build.py): workflow hanya butuh build.py dan isi data/; build.py membaca data/refill_pick.json dan data/extra/ langsung. SET UPLOAD MINIMAL = 4 file: build.py, data/refill_pick.json, data/extra/links_user.m3u, data/status_lokal.json. Folder staging ~/Downloads/gh_upload_1511 disiapkan (salinan, belum diunggah).
- Peringatan: PETA_FILE aturan 4 (build.py Mac punya modifikasi sendiri); upload membuat repo memakai build.py Mac itu. Jangan upload saat run workflow sedang berjalan (git push bisa bentrok).
- Menunggu go user untuk upload (dikerjakan manual via web, langkah diberikan setelah go). Hasil blok cek Pages dan riwayat repo: belum ada sampai output dikirim.
- Antrian: (1) go upload GitHub, lalu Run workflow dan cek playlist Pages, (2) STB/adb dan TiviMate, (3) cek R6 di Pages publik (hasil blok ini), (4) cek tab Actions, (5) Q3 dhanytv sebelum 19 Nov, (6) bandingkan status_github.json vs status_lokal.json, (7) rapikan handoff.

## STATUS TERBARU v47 (15 Nov, sekitar 13:30 WIB, EXIT chat v27) <- posisi akhir sebelum pindah chat. Menggantikan v46 untuk posisi terakhir; daftar AUDIT di v25 tetap berlaku.
- TERBUKTI (output Mac, 13:27 WIB): blok v46 jalan. Kalimat aturan tanpa survey masuk PESAN_PEMBUKA (grep = 1). Folder staging ~/Downloads/gh_upload_1511 berisi 4 file (build.py 22590 B, data/refill_pick.json 12537 B, data/extra/links_user.m3u 594 B, data/status_lokal.json 134120 B), salinan saja, belum diunggah. update.yml lokal SAMA dengan workflow repo.
- TERBUKTI (git log repo styleb0yz/iptv-playlist): commit playlist-bot d5b7374 (15 Nov 00:04:58 UTC), b5d61be (14 Nov 18:25 UTC), d4227a2 (14 Nov 09:57 UTC), ddfd379 (14 Nov 09:29 UTC); commit user: update.yml 14 Nov 17:04 WIB dan dua upload. last_run.txt = 2026-11-15T00:04:58Z. DUGAAN: commit bot tidak jatuh di jam cron (20:30, 04:30, 12:30 UTC), jadi run terjadwal telat jauh atau manual; run 04:30 UTC (11:30 WIB) 15 Nov belum ada commit saat dicek sekitar 13:27 WIB. Cek tab Actions.
- TERBUKTI (playlist publik Pages): 11849 EXTINF, 5 baris aflaxtv, group-title BERNOMOR ("01 · Indonesia · National TV"). Playlist lokal 11852 dan TANPA nomor. DUGAAN kuat: build.py Mac punya modifikasi yang membuang nomor di group-title (PETA_FILE aturan 4), jadi upload build.py ke repo akan menghapus nomor di Pages (R6); dibuktikan setelah upload dan Run workflow.
- RINGKASAN v39 sampai v45 (kalau heading-nya tidak ada di file): (a) Pasangan major, keputusan user opsi A (hasil revive merek mayor di folder utama berdekatan dengan kerabat, entri tetap terpisah). Mekanisme TERBUKTI di build.py: entri draft dikunci menurut nomor baris draft_esensial.csv; pick refill dikunci 5*10**5 + pos, jadi pick selalu di belakang draft kecuali pos dibuat pecahan negatif. R4d SELESAI di Mac (TS 1511_1304): Cinemax Asia Taiwan pos -499922.5 (tepat setelah Cinemax Classics), MTV India pos -499682.5 (tepat setelah MTV Spankin' New); total 11852, isi sama, urutan hanya berubah di Movies and Series dan Music. Backup: snapshot iptv_1511_1304, _arsip/out_sebelum_r4d_1511_1304, _arsip/refill_pick.json.sebelum_r4d_1511_1304. Rakuten Viki, Documentary+, Terra Mater WILD bukan mayor (tidak di major_brands.yml) jadi tetap. HBO (United States) dan HBO Hits TIDAK dipromosikan (keputusan user). refill.py menulis ulang refill_pick.json (DUGAAN: bisa menimpa pos); jangan jalankan refill.sh tanpa cek. (b) 5 baris aflaxtv: Indonesia Movie Channel (Vision+) di Archive Indonesia Local TV; HBO, HBO Hits, HBO Family, Cinemax di Archive Others (masing-masing punya kembaran IHT). (c) Latam, keputusan user opsi A: 15 varian Latin America tetap di folder utama (TERBUKTI tag ffprobe: 9 spa, 1 por, 1 eng, sisanya kosong, und, atau tanpa data); 9 baris latam di revive_siap tetap tidak dipromosikan. (d) Aturan baru user: jangan kirim survey atau tombol pilihan.
- Folder utama lokal 15 folder = 399 entri; Archive 56 grup, 11453 entri.
- Hitung jujur: channel bermasalah yang tertutup sekitar 10 dari 253 (4 persen); 185 CARI_LINK butuh link baru dari user atau app STB.
- ANTRIAN: (1) UPLOAD GITHUB, menunggu go user. Langkah web: buka https://github.com/styleb0yz/iptv-playlist, Add file, Upload files, seret isi ~/Downloads/gh_upload_1511 (build.py dan folder data dengan struktur data/ dan data/extra/ utuh), Commit. Pastikan tidak ada run berjalan di tab Actions. Lalu Actions, update-playlist, Run workflow. Setelah hijau cek Pages: hitung EXTINF, group-title tanpa nomor, aflaxtv 5, BeritaSatu dan Al-Iman ada. (2) STB/adb dan TiviMate dengan https://styleb0yz.github.io/iptv-playlist/playlist.m3u (tes BeritaSatu, Al-Iman TV, MTV India yang membawa http-referrer bhoomtv.org, Cinemax Asia Taiwan). (3) Tab Actions: kenapa commit bot tidak di jam cron. (4) Q3 dhanytv sebelum 19 Nov (jadwal habis 20 Nov 02:00 UTC). (5) Bandingkan status_github.json (repo 2.2 MB) dengan status_lokal.json. (6) Rapikan handoff (v35, v24, v19, v15 tidak ada; v20 ganda; cek apakah v39 sampai v41 tertulis; PETA_FILE bagian pembuka masih v5).

## STATUS TERBARU v48 (15 Nov, awal chat v28, setelah 14:10 WIB) <- hasil cek paket. Menggantikan v47 untuk posisi terakhir; daftar AUDIT v25 dan antrian v47 tetap berlaku.
- TERBUKTI (zip iptv_kirim_1511_1410): file terbaru handoff, log, PESAN_PEMBUKA jam 14:10 WIB. Pembuka v47 cocok dengan STATUS v47. Semua file yang disebut v47 ada. out/ dan gh_upload_1511 tidak ada di zip (memang dikecualikan).
- Heading v41, v35, v24, v19, v15 tidak ada; v20 ganda. v39 dan v40 ada.
- DUGAAN (dari handoff, belum diverifikasi di Mac): playlist lokal 11852, staging 4 file siap, Pages publik masih lama.
- Antrian tetap: (1) go upload GitHub, (2) STB/adb dan TiviMate, (3) tab Actions, (4) Q3 dhanytv sebelum 19 Nov, (5) status_github.json vs status_lokal.json, (6) rapikan handoff.

## STATUS TERBARU v49 (15 Nov, chat v28, go fase cari link web) <- Menggantikan v48 untuk posisi terakhir.
- TERBUKTI (docs/scrape_hasil.csv lama): scrape RRI Net ke rri.go.id gagal URLError; TVRI Sport dan SCTV tanpa URL m3u8/mpd di HTML/JS (SCTV ada tanda DRM).
- TERBUKTI (hasil web search): portal resmi RRI = rri.co.id; menu RRINet mengarah ke rri.co.id/stream/video. DUGAAN: halaman itu memuat URL stream; dites oleh scraper.
- Metode: Claude cari halaman resmi yang benar, scrape_situs.py di Mac menarik dan mengetes URL. Sandbox Claude tanpa jaringan. Urutan prioritas cari_link.csv: P1 (RRI Net, SCTV, Surau TV, TVRI Sport), P2 (7), P3 (17), P4 (155).
- Dikerjakan: baris RRI Net di data/situs_scrape.txt diganti ke https://rri.co.id/stream/video; backup file scrape lama di _arsip/*.sebelum_rri_TS.

## STATUS TERBARU v50 (15 Nov, chat v28) <- Menggantikan v49 untuk posisi terakhir.
- TERBUKTI (output Mac): scrape rri.co.id/stream/video menemukan 1 kandidat RRI Net HIDUP: https://stream-event.rri.go.id/memfs/8cec7b6a-22d6-44e6-adc6-2ee104f9f4e7.m3u8 (h264 1920x1080, aac, tanpa referer/token). Halaman memuat daftar stream lewat pola rri.co.id/stream/${item.link} (HTTPError) = DUGAAN lewat API. TVRI Sport dan SCTV tetap 0 kandidat. docs/scrape_siap.txt sekarang 4 baris (BeritaSatu x2, Al-Iman, RRI Net); versi lama di _arsip.
- DUGAAN: host stream-event/memfs adalah stream acara sementara, bukan RRI NET 24 jam. Belum dipromosikan. Dicek lewat manifest (MEDIA-SEQUENCE, ENDLIST) dan ffprobe.
- Antrian: (1) hasil cek manifest RRI Net, (2) Surau TV, (3) TVRI Sport lewat cara lain, (4) P2, P3, P4.

## STATUS TERBARU v51 (15 Nov, chat v28) <- Menggantikan v50 untuk posisi terakhir.
- TERBUKTI (output Mac): URL RRI Net stream-event adalah master playlist (satu varian 1920x1080, 5090800 bps, avc1+aac). URL varian membawa ?session=... (stream berbasis sesi, DUGAAN: bisa kadaluarsa). Tag live/event belum terlihat; dicek di playlist varian.
- Belum dipromosikan. Antrian: (1) hasil varian RRI Net, (2) Surau TV, (3) TVRI Sport, (4) P2 sampai P4.

## STATUS TERBARU v52 (15 Nov, 15:40 WIB, chat v28) <- Menggantikan v51 untuk posisi terakhir.
- TERBUKTI (output Mac): URL RRI Net stream-event LIVE real-time. Varian: target 2 detik, MEDIA-SEQUENCE 210785 lalu 210800 setelah 30 detik, tanpa ENDLIST/PLAYLIST-TYPE, PROGRAM-DATE-TIME sama dengan jam saat itu (08:37 UTC), HTTP 200 dua kali. URL master tanpa session dilayani server (session diberikan server per manifest).
- TERBUKTI (scrape_hasil.csv): URL ditemukan di halaman resmi rri.co.id/stream/video.
- DUGAAN: isi bisa saja siaran acara, bukan RRI NET 24 jam; umur session belum diuji. Belum dipromosikan. Dicek lewat 3 gambar dari stream.
- Antrian: (1) lihat isi stream RRI Net, lalu go promosi (links_user.txt, cek_link_baru.py, build), (2) Surau TV, (3) TVRI Sport, (4) P2 sampai P4.

## STATUS TERBARU v53 (15 Nov, 15:45 WIB, chat v28) <- Menggantikan v52 untuk posisi terakhir.
- TERBUKTI (output Mac): ffmpeg mengambil 3 gambar dari stream RRI Net stream-event (/tmp/rri_f1.jpg 39271 B, f2 51372 B, f3 163822 B, jam 15:43-15:44 WIB). DUGAAN: ukuran beda = konten berubah. Isi gambar belum dilaporkan; belum dipromosikan.
- Blok v52 sempat tampak tercetak dua kali di terminal; entri dobel (kalau ada) dibuang oleh blok v53, backup di _arsip/*.sebelum_dedup_*.
- Antrian: (1) isi gambar RRI Net lalu go promosi, (2) Surau TV, (3) TVRI Sport, (4) P2 sampai P4.

## STATUS TERBARU v54 (15 Nov, chat v28) <- Menggantikan v53 untuk posisi terakhir.
- TERBUKTI (LyngSat via web search): domain resmi Surau TV = surautv.id (TV streaming Islami asal Padang). Scrape surautv.id dijalankan.
- DUGAAN: SCTV streaming resmi hanya lewat Vidio atau IndiHome (khusus pelanggan), buntu untuk scraper; TVRI Sport sudah dua kali 0 kandidat. Keduanya diparkir (butuh link dari user atau app STB).
- Menunggu: laporan isi 3 gambar RRI Net dari user sebelum promosi.
- Antrian: (1) isi gambar RRI Net lalu go promosi, (2) hasil scrape Surau TV, (3) P2 sampai P4.

## STATUS TERBARU v55 (15 Nov, chat v28) <- Menggantikan v54 untuk posisi terakhir.
- TERBUKTI (output Mac): scrape surautv.id = 0 kandidat. Scraper buntu untuk Surau TV, SCTV, TVRI Sport (player dinamis/embed/DRM, DUGAAN). docs/scrape_siap.txt tetap 4 link HIDUP (BeritaSatu x2, Al-Iman, RRI Net); backup sebelum scrape di _arsip/*.sebelum_surau_*.
- Hasil fase cari link web P1: 1 kandidat baru (RRI Net, live real-time, isi belum dilaporkan user). Penilaian: web+scraper hasilnya tipis; jalur terbesar = app bawaan STB via adb (R3a, belum dijalankan).
- Antrian: (1) laporan isi gambar RRI Net lalu go promosi, (2) go STB/adb (R3a), (3) P2 sampai P4 lewat web bila perlu, (4) upload GitHub.

## STATUS TERBARU v56 (15 Nov, chat v28) <- Menggantikan v55 untuk posisi terakhir.
- Keputusan user (ucapan "rri aman"): isi stream RRI Net dianggap aman (DUGAAN: gambar belum dilihat Claude). Belum dipromosikan sampai user bilang go.
- TERBUKTI (web search): playlist i.mjh.nz untuk Pluto, Samsung TV Plus, Plex, Stirr, PBS dicabut setelah klaim DMCA Warner (TorrentFreak Agu 2024; forum Channels DVR: m3u8 404). Jalur FAST playlist ditolak (abu-abu, dan stream-nya sudah ada lewat iptv-org). Proyek hanya memakai EPG i.mjh.nz.
- TERBUKTI (README): Free-TV/IPTV punya playlist.m3u8 (raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8), hanya channel resmi gratis. DUGAAN: tanpa channel kabel berbayar (Fox News, HBO, AMC).
- Dikerjakan: ukur kecocokan nama Free-TV vs 185 CARI_LINK di /tmp (baca saja).
- Antrian: (1) go promosi RRI Net, (2) hasil ukur Free-TV, (3) go STB/adb R3a, (4) upload GitHub.

## STATUS TERBARU v57 (15 Nov, chat v28) <- Menggantikan v56 untuk posisi terakhir.
- TERBUKTI (output Mac): Free-TV playlist.m3u8 = 2203 entri; 32 baris cocok persis dengan cari_link.csv (sekitar 26 channel unik; Al-Iman TV dan BeritaSatu sudah beres); 73 baris mirip (mayoritas salah channel, diabaikan).
- Disaring: TBS (itu TBS Jepang), CNBC (hanya youtube.com/live), AMC dan ITV2/3/4, Channel 5, France 5 (URL IP mentah = DUGAAN restream tidak resmi) tidak dites. Tanda Ⓖ = geoblok, DUGAAN banyak gagal dari Indonesia.
- Tambahan manual: stream BBC News worldwide (push-ww-live) untuk BBC News Europe dan BBC News UK HD. RRI Net (stream-event) ikut dites.
- Dikerjakan: kandidat ditambah ke data/links_user.txt (backup di _arsip/*.sebelum_freetv_*), lalu python3 cek_link_baru.py (baca saja; hasil di docs/cek_link_baru.csv).
- Antrian: (1) hasil tes, (2) go promosi yang HIDUP (RRI Net dan Free-TV), (3) go STB/adb R3a, (4) upload GitHub.

## STATUS TERBARU v58 (15 Nov, chat v28) <- Menggantikan v57 untuk posisi terakhir.
- TERBUKTI (output Mac, cek_link_baru.py): 24 link, 11 HIDUP. Baru hidup: La 2, La 1, GB News, TV5Monde Info, Vevo Pop, BBC News Europe (URL sama untuk BBC News UK HD), RRI Net, Discovery Channel (feed Italia, DUGAAN IT_SIM). Mati 403 (geoblok): BBC Four/Parliament/Scotland/Three, DR1, Canale 5, ZDFneo, arte x2, Al Jazeera Documentary, GREAT! movies/romance. Mati 400: TRT 1. Diparkir tanda "butuh VPN" (tidak dihitung target).
- Hitung kasar: kalau semua hidup dipromosikan sekitar 19 dari 253 (7 persen), DUGAAN karena irisan nama belum dicek.
- Belum dipromosikan. Mekanisme promosi: tambah entri ke data/refill_pick.json (brand, label, folder, pos, url, region, src_name, height), lalu build (pola R4 tahap 2, backup dulu).
- Antrian: (1) cek bahasa audio Discovery dan nama folder rules.yml (blok v58), (2) go promosi, (3) go STB/adb R3a, (4) upload GitHub.

## STATUS TERBARU v59 (15 Nov, chat v28) <- Menggantikan v58 untuk posisi terakhir.
- TERBUKTI (output Mac): baris HIDUP di cek_link_baru.csv: La 2 720p, GB News 1080p, La 1 720p, TV5Monde Info 1080p, Vevo Pop 1080p, BBC News Europe 720p (eng), RRI Net 1080p, Discovery Channel 1080p. Tag audio kosong untuk Discovery dan TV5Monde (data tes, bukan bukti bahasa).
- TERBUKTI (kode dan status_lokal.json): La 2 dan RRI Net adalah baris draft folder utama; URL lama La 2 gagal 403 Geoblock (cek 13 Nov). Jalur promosi: tahap 1 (extra/links_user.m3u dengan tvg-id sama dengan draft). Channel Archive (La 1, GB News, TV5Monde Info, BBC News Europe, Vevo Pop): extra/links_user.m3u plus data/refill_pick.json (kunci pick = URL, build.py baris 309-325). BBC News UK HD satu URL dengan Europe, jadi satu entri.
- Keputusan: Discovery Channel DITAHAN (dua baris Discovery di daftar, feed Free-TV = Italia DUGAAN, audio tidak terbukti). 7 channel direncanakan: RRI Net, La 2, La 1, GB News (folder uk), TV5Monde Info, BBC News Europe (intl_news), Vevo Pop (music).
- DUGAAN: cek github_dead_after_fails dari runner GitHub bisa menganggap URL geoblok-dari-US mati lalu memindahkannya ke Likely Dead.
- Dry-run tertulis ke /tmp/promosi_links.m3u dan /tmp/promosi_pick.json; belum ada file data berubah. Menunggu go.

## STATUS TERBARU v60 (15 Nov, EXIT chat v28) <- posisi akhir sebelum pindah chat. Menggantikan v59 untuk posisi terakhir; daftar AUDIT v25 tetap berlaku.
- TERBUKTI (output Mac): dry-run promosi jalan. 7 entri extra disiapkan (RRI Net situs resmi, La 2, La 1, GB News, TV5Monde Info, BBC News Europe, Vevo Pop) dengan tvg-id dan logo dipinjam dari index.m3u. 5 pick: europe La 1 pos 1650, uk GB News pos 1440, intl_news TV5Monde Info pos 1240 dan BBC News Europe pos 1250, music Vevo Pop pos 1750. RRI Net dan La 2 tidak butuh pick (baris draft folder 01 dan 11, jalur tahap 1). Hasil disimpan di docs/promosi_links_dryrun.m3u dan docs/promosi_pick_dryrun.json. BELUM DI-APPLY: data/extra/links_user.m3u dan data/refill_pick.json belum berubah.
- Rencana apply (menunggu go user): backup (bash backup.sh, _arsip/out_sebelum_R5a_TS, salin refill_pick.json dan links_user.m3u), tambah baris dry-run (tanpa #EXTM3U) ke data/extra/links_user.m3u, gabung 5 pick ke data/refill_pick.json (cek URL tidak dobel), build, cek total EXTINF dan folder 01, 10, 11, 08, 13, lalu laporkan.
- TERBUKTI (tes cek_link_baru.py): 24 link, 11 HIDUP. Mati 403 geoblok (diparkir "butuh VPN", tidak dihitung): BBC Four, BBC Parliament, BBC Scotland, BBC Three, DR1, Canale 5, ZDFneo, arte x2, Al Jazeera Documentary, GREAT! movies, GREAT! romance. TRT 1 error 400. Discovery Channel DITAHAN (dua baris Discovery, feed Free-TV = Italia DUGAAN, audio tidak terbukti). BBC News UK HD satu URL dengan BBC News Europe (satu entri).
- TERBUKTI (scrape): RRI Net HIDUP dari rri.co.id/stream/video (stream-event, live real-time, sequence naik, tanpa ENDLIST); user bilang isi aman. Surau TV, SCTV, TVRI Sport: scraper buntu (0 kandidat).
- TERBUKTI (web search): playlist i.mjh.nz untuk Pluto, Samsung TV Plus, Plex, Stirr, PBS dicabut setelah klaim DMCA; jalur FAST ditolak (hanya EPG i.mjh.nz dipakai). Free-TV/IPTV (raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8): 2203 entri, 32 cocok persis dengan 185 CARI_LINK. Dibuang: AMC dan ITV2/3/4, Channel 5, France 5 (URL IP mentah, DUGAAN restream tidak resmi), TBS (TBS Jepang), CNBC (hanya YouTube). Daftar mirip (73) diabaikan (mayoritas salah channel).
- Hitung kasar: sekitar 10 tertutup sebelumnya + 7 channel (UK HD ikut tercover) = sekitar 17 sampai 19 dari 253 (7 persen) kalau apply jadi dan semua tetap hidup (DUGAAN). Target 90 persen jauh; 185 CARI_LINK tetap butuh link dari user atau app STB. Jalur terbesar yang belum jalan: STB via adb (R3a).
- DUGAAN: cek github_dead_after_fails dari runner GitHub (AS) bisa memindahkan URL yang geoblok dari AS ke Likely Dead; belum terukur.
- Antrian: (1) go apply promosi 7 channel (dry-run di docs/), (2) tes TiviMate/STB untuk RRI Net dan pick baru, (3) STB/adb R3a, (4) P2 sampai P4 cari link lewat web (cari_link.csv: P2 7, P3 17, P4 155; pakai situs resmi, scrape_situs.py), (5) upload GitHub (set minimal 4 file di ~/Downloads/gh_upload_1511; segarkan salinan setelah apply: build.py, data/refill_pick.json, data/extra/links_user.m3u, data/status_lokal.json), Run workflow, cek Pages (11852+, group-title tanpa nomor), (6) cek tab Actions (commit bot tidak di jam cron), (7) Q3 dhanytv sebelum 19 Nov, (8) status_github.json vs status_lokal.json, (9) rapikan handoff (v41, v35, v24, v19, v15 tidak ada; v20 ganda; PETA_FILE pembuka masih v5).

## STATUS TERBARU v61 (15 Nov, awal chat v29) <- Menggantikan v60 untuk posisi terakhir; daftar AUDIT v25 tetap berlaku.
- TERBUKTI (cek paket): zip 15 Nov 16:39 WIB (nama 1511_1639 cocok), pembuka v60 = STATUS v60, 65 file, refill_pick.json dan links_user.m3u belum berubah sebelum apply.
- DUGAAN: file disebut handoff tapi tidak ada di zip: status_github.json, data/last_run.txt, data/extra/NAMA.m3u, fase_b.py, keys.sh, GUIDES.md, laporan.md (konteks belum dibuka).
- User bilang ikut rencana: apply promosi 7 channel dijalankan lewat blok Terminal (backup, tambah 7 entri ke data/extra/links_user.m3u, gabung 5 pick ke data/refill_pick.json, build, cek). Hasil dilaporkan di balasan berikut.

## STATUS TERBARU v62 (15 Nov, chat v29) <- Menggantikan v61 untuk posisi terakhir.
- TERBUKTI (output Mac): apply R5a jalan. Backup snapshot iptv_1511_1643 dan _arsip/out_sebelum_R5a. refill_pick.json 51 jadi 56. links_user.m3u 9 entri. Build OK: masuk 12539, playlist 11858 (sebelumnya 11852), duplikat 681, ditahan 0.
- TERBUKTI: URL baru ada di out/playlist.m3u untuk TV5Monde Info (International News), GB News (UK Main TV), Vevo Pop (Music), RRI Net dan BBC News Europe (grup lengkap belum terlihat).
- BELUM TERBUKTI: La 1 dan La 2 baru (grep awal salah pola); +6 dari 7 entri (DUGAAN: baris draft menggantikan). Entri lama channel yang sama masih ada di grup Archive (Likely Dead).
- Antrian: verifikasi per URL, tes TiviMate/STB, adb R3a, P2-P4, upload GitHub (segarkan 4 file), Actions, Q3 dhanytv sebelum 19 Nov, status_github.json, rapikan handoff.

## STATUS TERBARU v63 (15 Nov, chat v29) <- Menggantikan v62 untuk posisi terakhir.
- TERBUKTI (output Mac): R5a sudah apply, playlist 11858. URL baru ada di folder utama untuk RRI Net (Indonesia National TV), La 1 (Europe Main TV), GB News (UK Main TV), TV5Monde Info dan BBC News Europe (International News), Vevo Pop (Music). La 2 di Europe Main TV memakai URL lama voxel (status_lokal ok=true, 720p); URL promosi la2_main_dvr kalah ranking karena belum dites.
- TERBUKTI: sudah revive dan di folder utama: BeritaSatu (Indonesia News, stream sama dengan BTV), Al-Iman TV (Islam Indonesia dan Haramain), RRI Net, La 1, GB News, TV5Monde Info, BBC News Europe, Vevo Pop, plus La 2 (URL lama). Belum dites di TiviMate/STB.
- TERBUKTI: docs/revive_kerja.csv adalah foto R3a sebelum R4 dan R5a; kolom aksi tidak diperbarui, jadi channel yang sudah direvive masih tertulis CARI_LINK di sana.
- DUGAAN: daftar chat v29 mencampur channel yang sudah aman (SUDAH_TERCOVER 25, TUNGGU_STB 10, latam 15, radio di folder Radio) dengan yang belum. Hitungan 7 sampai 8 mengabaikan SUDAH_TERCOVER; handoff v60 menulis sekitar 10 tertutup dan 17 sampai 19 dari 253. Definisi tertutup harus dikunci.
- DUGAAN (cocok nama): 144 dari 213 Likely Dead punya slot di draft_esensial.csv; 69 tidak punya slot draft atau refill_pick (varian regional: West, Latin America, Asia, India, UK dll).
- Permintaan user: satu daftar bersih per channel (aman atau belum, lokasi sekarang, folder tujuan), dicocokkan per URL, dan semua channel tanpa slot dimasukkan ke slot folder (termasuk PROMOSI_ALT, TES_ALT, SUDAH_TERCOVER). Rencana: docs/revive_status_1511.csv dan usulan aturan slot untuk 69 channel. Belum ada perubahan rules.yml atau draft; menunggu konfirmasi user.
- Antrian: (1) konfirmasi maksud user, (2) revive_status_1511.csv, (3) slot untuk 69 channel, (4) tes_lokal.sh untuk URL baru, (5) tes TiviMate/STB, (6) adb R3a, (7) upload GitHub, (8) Actions, (9) Q3 sebelum 19 Nov, (10) status_github.json, (11) rapikan handoff.

## STATUS TERBARU v64 (15 Nov, chat v29) <- Menggantikan v63 untuk posisi terakhir.
- TERBUKTI (sandbox, data = iptv.zip 16:43 WIB, playlist 11858): revive_status.py (baru, baca saja) menulis docs/revive_status_1511.csv (268 baris, dicocokkan per URL, kolom status_baru, folder_sekarang, folder_tujuan) dan docs/usulan_slot_1511.csv (69 baris format draft_esensial.csv). Tidak ada perubahan playlist, rules.yml, atau draft.
- TERBUKTI (sandbox): aman dari 253 = 41 (28 lolos tes lokal Mac, 13 URL baru belum dites lokal) = 16,2 persen; target 90 persen = 228. TUNGGU_STB 10 (belum dihitung aman), BELUM_SLOT_ADA_URL_MATI 25, BELUM_ALT_LOLOS_DI_ARSIP 4 (HGTV US, Nickelodeon India, Nickelodeon UK, Sony Channel Argentina), BELUM 173, KEPUTUSAN_LATAM 15.
- TERBUKTI: likely_dead tanpa slot draft/rules = 69 (cocok nama + refill_pick + gaps), sama dengan angka v63. Usulan folder: induk 37, kata kunci 18, negara 14. Usulan = DUGAAN sampai lo cek.
- Definisi dikunci: AMAN = ada URL di folder utama 01-15 yang lolos tes lokal atau belum dites tapi tidak gagal di tes ketat/R3a; belum dites di TiviMate/STB.
- Antrian: (1) cek output Mac sama dengan sandbox, (2) lo review usulan_slot_1511.csv, (3) go tambah slot ke draft, (4) tes_lokal.sh untuk URL baru, (5) STB/adb R3a, (6) upload GitHub, (7) Actions, (8) Q3 sebelum 19 Nov, (9) status_github.json, (10) rapikan handoff.

## STATUS TERBARU v65 (15 Nov, chat v29) <- Menggantikan v64 untuk posisi terakhir. KOREKSI v64.
- TERBUKTI: v64 salah soal BELUM_ALT_LOLOS_DI_ARSIP 4 (HGTV US, Nickelodeon India dan UK, Sony Channel Argentina). Pencocokan arsip hanya pakai nama tanpa cek negara, jadi cocok ke Nickelodeon Brasil dan Sony Channel Brasil (bahasa Portugis). HGTV US hanya punya feed i.mjh.nz (ditolak DMCA, v28). Sudah ditambal (cek negara), hasil: ALT_LOLOS_DI_ARSIP = 0, BELUM = 177. Aman tetap 41 dari 253 (16,2 persen).
- TERBUKTI: tidak ada alternatif arsip yang layak dipromosi, jadi dry-run promosi 4 channel dibatalkan. 69 channel tanpa slot: hanya 15 yang sudah hidup di folder utama lewat varian lain, 52 mati. Slot untuk yang mati tidak menaikkan persen revive dan tidak dikerjakan.
- Jalur ke 90 persen: link baru untuk 177 BELUM (STB/adb R3a, sumber web), tes STB untuk 10 TUNGGU_STB, 13 URL baru belum dites lokal (tes_lokal.sh), 15 KEPUTUSAN_LATAM butuh keputusan user.
- Antrian: (1) tes_lokal.sh untuk 13 URL baru, (2) STB/adb R3a, (3) tes TiviMate/STB, (4) upload GitHub, (5) Actions, (6) Q3 sebelum 19 Nov, (7) status_github.json, (8) rapikan dan pangkas handoff, (9) cek ukuran backup.

## STATUS TERBARU v66 (15 Nov, chat v29) <- Menggantikan v65 untuk posisi terakhir.
- TERBUKTI (output Mac): backup.sh rsync tidak mengecualikan _arsip, jadi tiap snapshot 46 MB dan 15 snapshot 337 MB dari backup 381 MB. Ditambal: backup.sh sekarang --exclude '/_arsip' (salinan lama: _arsip/backup.sh.sebelum-v66).
- Pruning dijalankan: 12 snapshot lama dihapus (sisa 1511_1410, 1511_1643, 1511_2200 plus yang baru dari kirim.sh), 3 _arsip/out_sebelum_* lama dihapus (sisa out_sebelum_r4d_1511_1304). Zip lama di ~/IPTV_BACKUP/zip dibiarkan (8,9 MB). Angka sesudah ada di output du; DUGAAN total sekitar 100 MB di luar trash-rescue (79 MB, isi belum diputuskan).
- Antrian: (1) tentukan nasib trash-rescue, (2) apply 69 slot dari docs/usulan_slot_1511.csv ke draft_esensial.csv (tunggu go; kecualikan LatAm audio Spanyol, varian India/Asia di folder Barat, TVRI 480p), (3) tes_lokal.sh untuk 13 URL baru, (4) STB/adb R3a, (5) tes TiviMate/STB, (6) upload GitHub, (7) Actions, (8) Q3 sebelum 19 Nov, (9) status_github.json, (10) pangkas handoff.

## STATUS TERBARU v67 (15 Nov, chat v29) <- Menggantikan v66 untuk posisi terakhir.
- TERBUKTI (output Mac): pruning jalan, IPTV_BACKUP 381 MB turun ke 228 MB, snapshot 337 MB ke 137 MB (3 snapshot lama masih sekitar 46 MB, yang baru 3,9 MB), _arsip 42 MB ke 14 MB. trash-rescue (79 MB) belum disentuh: isinya 3 folder iptv lama, 5 zip lama, iptv.zip, tivimate.apk (21 MB, kemungkinan masih dibutuhkan untuk STB).
- Apply 69 slot dari docs/usulan_slot_1511.csv ke draft_esensial.csv (backup: _arsip/draft_esensial.csv.sebelum-v67). TERBUKTI (sandbox): build sebelum dan sesudah identik, 11858 channel, 0 URL berubah, 0 pindah folder. Slot hanya menyiapkan tempat; channel mati baru masuk folder utama kalau ada link hidup. Hasil build Mac dicatat di chat.
- ~/Downloads/gh_upload_1511 = folder staging upload GitHub (4 file: build.py, data/refill_pick.json, data/extra/links_user.m3u, data/status_lokal.json). Perbandingan dengan file sekarang dijalankan di blok v67; BEDA berarti staging basi dan harus disegarkan sebelum upload.
- Antrian: (1) nasib trash-rescue dan 2 snapshot lama, (2) segarkan gh_upload_1511 bila BEDA, (3) tes_lokal.sh untuk 13 URL baru, (4) STB/adb R3a, (5) tes TiviMate/STB, (6) upload GitHub, (7) Actions, (8) Q3 sebelum 19 Nov, (9) status_github.json, (10) pangkas handoff.

## STATUS TERBARU v68 (16 Nov, chat v29) <- Menggantikan v67 untuk posisi terakhir.
- TERBUKTI (output Mac): apply 69 slot jalan (draft_esensial.csv 423 baris, backup _arsip/draft_esensial.csv.sebelum-v67), build ulang tetap 11858 channel, sama dengan sandbox.
- TERBUKTI (output Mac): gh_upload_1511 basi. data/refill_pick.json dan data/extra/links_user.m3u BEDA dari file sekarang (sebelum R5a); build.py dan data/status_lokal.json SAMA. Segarkan dua file itu sebelum upload GitHub.
- Pruning sisa dijalankan: snapshot 1511_1410 dan 1511_1643 dihapus (sisa 1511_2200, 1511_2353, 1611_0000), trash-rescue dikosongkan kecuali tivimate.apk. Ukuran sesudah ada di output du di chat.
- Sisa waktu: Q3 dhanytv sebelum 19 Nov (3 hari lagi per 16 Nov).
- Antrian: (1) segarkan gh_upload_1511 (2 file BEDA), (2) tes_lokal.sh untuk 13 URL baru, (3) STB/adb R3a, (4) tes TiviMate/STB, (5) upload GitHub, (6) Actions, (7) Q3 sebelum 19 Nov, (8) status_github.json, (9) pangkas handoff.

## STATUS TERBARU v69 (16 Nov, chat v29) <- Menggantikan v68 untuk posisi terakhir.
- KUNCI FOKUS (keluhan user, wajib dibawa ke semua chat sampai selesai): hanya revive likely dead, stream bermasalah, dan foldering. Dilarang menawarkan hal sampingan (pruning, arsip, upload GitHub, rapikan handoff, tawaran "gas ini gas itu") kecuali user yang minta. Selesai = tiap channel punya status akhir HIDUP, TUNGGU_STB, atau MATI_PERMANEN dengan alasan. Setiap balasan buka dengan angka progres dan satu langkah berikutnya yang menambah channel hidup. Sesi chat v29 hampir semuanya pembukuan dan menghasilkan 0 channel hidup baru; itu keluhan user.
- TERBUKTI (sandbox, out/playlist.m3u): nomor di group-title sudah hilang, 0 dari 11858 berawalan angka. Pages publik masih lama bernomor (belum upload). DUGAAN: urutan folder di TiviMate tanpa nomor mengikuti urutan playlist, belum dites di STB.
- Angka: 41 dari 253 aman, 177 BELUM, 25 slot ada URL mati, 10 TUNGGU_STB, 15 latam menunggu keputusan user. Target 90 persen = 228.
- Antrian revive (urut): (1) tes_lokal.sh untuk 13 URL baru, (2) STB/adb R3a, (3) tes 10 TUNGGU_STB di TiviMate, (4) VPN untuk sekitar 9 geoblok, (5) minta link user untuk 25 slot URL mati, (6) tulis status akhir per channel di docs/revive_status_1511.csv. Deadline user: Q3 dhanytv sebelum 19 Nov, dikerjakan hanya kalau user minta.

## STATUS TERBARU v69 (16 Nov, chat v29) <- Menggantikan v68 untuk posisi terakhir.
- KUNCI FOKUS (keluhan user, wajib dibawa ke semua chat sampai selesai): hanya revive likely dead, stream bermasalah, dan foldering. Dilarang menawarkan hal sampingan (pruning, arsip, upload GitHub, rapikan handoff, tawaran "gas ini gas itu") kecuali user yang minta. Selesai = tiap channel punya status akhir HIDUP, TUNGGU_STB, atau MATI_PERMANEN dengan alasan. Setiap balasan buka dengan angka progres dan satu langkah berikutnya yang menambah channel hidup. Sesi chat v29 hampir semuanya pembukuan dan menghasilkan 0 channel hidup baru; itu keluhan user.
- TERBUKTI (sandbox, out/playlist.m3u): nomor di group-title sudah hilang, 0 dari 11858 berawalan angka. Pages publik masih lama bernomor (belum upload). DUGAAN: urutan folder di TiviMate tanpa nomor mengikuti urutan playlist, belum dites di STB.
- Angka: 41 dari 253 aman, 177 BELUM, 25 slot ada URL mati, 10 TUNGGU_STB, 15 latam menunggu keputusan user. Target 90 persen = 228.
- Antrian revive (urut): (1) tes_lokal.sh untuk 13 URL baru, (2) STB/adb R3a, (3) tes 10 TUNGGU_STB di TiviMate, (4) VPN untuk sekitar 9 geoblok, (5) minta link user untuk 25 slot URL mati, (6) tulis status akhir per channel di docs/revive_status_1511.csv. Deadline user: Q3 dhanytv sebelum 19 Nov, dikerjakan hanya kalau user minta.

## STATUS TERBARU v70 (16 Nov, chat v29) <- Menggantikan v69 untuk posisi terakhir.
- TERBUKTI (user, tes STB): iNews di folder 02 (live.i-news.tv/hls/stream.m3u8) memutar iNews Arab, salah channel. Trans TV di folder 01 (proxy-v.rctiplus.id/live/web/transtv) memutar channel drama Vision+, salah channel. ANTV (proxy-v.rctiplus.id/live/web/antv) jalan. SCTV tidak jalan (202.150.172.59/SCTV, tes lokal juga gagal). Indosiar (dens.tv/h/h207) DUGAAN tidak jalan, user belum yakin.
- TERBUKTI (data): iNews dan Trans TV lolos tes lokal tapi salah isi, jadi lolos lokal BUKAN bukti channel benar; identitas hanya bisa dipastikan di STB. Angka aman 41 dari 253 kemungkinan menggelembung. Estimasi sekitar 42 (ANTV naik dari TUNGGU_STB), 41 kalau Indosiar mati.
- Kandidat baru (belum dites): Trans TV dari video.detik.com/transtv/smil:transtv.smil/playlist.m3u8 (di Archive Indonesia Local, nama Trans TV cad). iNews Indonesia belum ada kandidat di data (satu-satunya lain: INews India pishow.tv, bukan yang dicari). SCTV dan Indosiar belum ada kandidat hidup.
- Rencana ganti player: TiviMate ke Kepler Player. Fitur Kepler belum terverifikasi (pencarian web tidak menemukan halaman spesifik). Tes 4 cek di STB: (1) waktu import 11858 entri, (2) urutan folder tanpa nomor, (3) 5 channel Indonesia (iNews, Trans TV, ANTV, SCTV, Indosiar), (4) satu channel DRM atau MPD dari TUNGGU_STB. Belum ada perubahan playlist untuk Kepler.
- GitHub belum diupdate, gh_upload_1511 basi (refill_pick.json dan links_user.m3u BEDA).
- Antrian revive (urut): (1) tes curl di Mac untuk Trans TV detik dan kandidat slug rctiplus (inews, sctv, indosiar), (2) perbaiki 5 channel Indonesia di folder 01 dan 02, (3) STB/adb R3a, (4) tes_lokal.sh 13 URL baru, (5) tes Kepler 4 cek, (6) tes 9 TUNGGU_STB sisa, (7) VPN geoblok, (8) status akhir per channel.

## STATUS TERBARU v71 (16 Nov, chat v29) <- Menggantikan v70 untuk posisi terakhir.
- TERBUKTI (output Mac): kesiapan folder lolos. 17 file kunci ada, playlist 11858, 0 group bernomor, urutan folder benar (Indonesia National TV, News, Islam, Football, ... lalu Archive). gh_upload_1511 basi (refill_pick.json dan links_user.m3u BEDA). KUNCI FOKUS tercatat 2 kali di PESAN_PEMBUKA.txt dan handoff (duplikat, kemungkinan blok v69 jalan dua kali; tidak merusak).
- TERBUKTI (keplerplayer.com): Kepler mendukung M3U link dan file (termasuk USB), XMLTV, update otomatis harian per playlist, editor playlist (sembunyikan group), Android TV/Google TV/Fire TV, 30 hari semua fitur gratis lalu versi gratis dengan satu playlist, live TV, guide, search; Pro berbayar (tahunan atau lifetime). Klaim vendor: katalog 250.000 entri refresh sekitar 32 detik di Android TV. DRM/MPD tidak disebut di situs, belum diketahui. Playlist tidak perlu diubah untuk Kepler; tes STB 4 cek tetap berlaku. Folder Archive bisa disembunyikan lewat editor Kepler (DUGAAN fitur editor mungkin Pro).
- Langkah revive berjalan: tes curl kandidat Indonesia (hasil di docs/curl_tes_1611.txt). Slug rctiplus inews, inewstv, sctv, indosiar adalah tebakan (DUGAAN). curl hanya membuktikan stream ada, bukan channel benar; identitas dikonfirmasi user di STB.
- Antrian revive (urut): (1) baca hasil curl, (2) perbaiki 5 channel Indonesia folder 01 dan 02, (3) STB/adb R3a, (4) tes_lokal.sh 13 URL baru, (5) tes Kepler 4 cek, (6) 9 TUNGGU_STB sisa, (7) VPN geoblok, (8) status akhir per channel.

## STATUS TERBARU v72 (16 Nov, chat v29) <- Menggantikan v71 untuk posisi terakhir.
- TERBUKTI (docs/curl_tes_1611.txt): curl tanpa header ke proxy-v.rctiplus.id semua 403 "denied by Referer ACL" (termasuk ANTV yang jalan di STB), jadi tebakan slug inews, inewstv, sctv, indosiar belum terbukti apa pun; tes harus kirim Referer (visionplus.id atau rctiplus.com). video.detik.com Trans TV HTTP 000 (tidak tersambung dari Mac, sebab belum diketahui). live.i-news.tv 200 hidup 1080p tapi channel salah (Arab). dens.tv h207 200 hidup.
- TERBUKTI (data): dens.tv h207 dipakai dua nama, Indosiar HD dan MOJI TV HD (h207/index.m3u8). DUGAAN: URL Indosiar sebenarnya Moji TV, itu sebab "tidak jalan" di STB. Menunggu konfirmasi user apa yang tayang di STB. Kandidat dens.tv lain di data: tidak ada SCTV, Trans TV, atau iNews.
- TERBUKTI (out/playlist.m3u): 1414 baris opsi header (EXTVLCOPT, EXTHTTP, KODIPROP). ANTV = Widevine + Referer visionplus.id + license pihak ketiga vision.mikrofast.web.id (rapuh, DUGAAN). Trans TV = ClearKey + Referer rctiplus.com, tayang salah channel. Indosiar dens.tv = header DENSGO (UA, Origin, Referer). Risiko Kepler: dukungan header dan DRM tidak disebut di keplerplayer.com; tes Kepler utama pakai ANTV dan Indosiar.
- Estimasi aman: sekitar 41 dari 253 (ANTV naik, Indosiar kemungkinan turun). Belum ada channel hidup baru dari curl.
- Antrian revive (urut): (1) user konfirmasi isi Indosiar di STB (Moji TV atau bukan), (2) betulkan label: Indosiar jadi MATI/BELUM dan Moji TV pindah ke folder yang benar jika terbukti, (3) Trans TV dan iNews dicabut dari folder 01 dan 02 sebagai BELUM, (4) cari link SCTV, Indosiar, Trans TV, iNews yang benar (web, curl dengan Referer), (5) STB/adb R3a, (6) tes Kepler (ANTV, Indosiar, 1 DRM), (7) 9 TUNGGU_STB sisa, (8) VPN geoblok, (9) status akhir per channel.

## STATUS TERBARU v73 (16 Nov, chat v29) <- Menggantikan v72 untuk posisi terakhir.
- TERBUKTI (user, STB): Indosiar (dens.tv h207) tampil hitam dengan 403/404, bukan Moji TV. Hipotesis salah label (v72) tidak terbukti. DUGAAN: segment ditolak karena header DENSGO (UA, Origin, Referer) tidak lengkap di player. Tes segment dengan dan tanpa header ada di docs/curl_seg_1611.txt.
- Estimasi aman: sekitar 41 dari 253 (ANTV naik, Indosiar turun jadi gagal di STB).

## STATUS TERBARU v74 (16 Nov, chat v29) <- Menggantikan v73 untuk posisi terakhir.
- TERBUKTI (docs/curl_seg_1611.txt): segment Indosiar dens.tv HTTP 000 (gagal konek, 0 byte) dengan dan tanpa header DENSGO, jadi dugaan header (v73) gugur. Playlist 200 tapi segment tidak terambil dari Mac. status_lokal mencatat Indosiar lolos 14 Nov 11:40 UTC, jadi stream kemungkinan mati atau diblokir sejak itu (DUGAAN).
- TERBUKTI: ANTV proxy-v.rctiplus.id 403 tanpa Referer, 200 dengan Referer https://www.visionplus.id/. ANTV jalan di TiviMate karena referrer dari playlist diteruskan. Tes Kepler wajib: dukungan Referer (ANTV).
- TERBUKTI (data): 662 status di status_lokal.json bertanggal 13 sampai 14 Nov, jadi angka aman 41 berbasis tes 2 hari lalu dan kemungkinan menggelembung. Dijalankan tes_lokal.sh (13 URL baru) dan revive_status.py ulang; backup _arsip/status_lokal.json.sebelum-1611. Hasil angka baru dicatat di chat.
- Antrian revive (urut): (1) tes ulang seluruh folder 01-15 supaya angka aman jujur (tes_ketat atau tes_lokal.sh semua), (2) cabut Indosiar, Trans TV, iNews dari folder utama sebagai BELUM, (3) cari link SCTV, Indosiar, Trans TV, iNews (curl dengan Referer), (4) STB/adb R3a, (5) tes Kepler (ANTV Referer, 1 DRM), (6) 9 TUNGGU_STB sisa, (7) VPN geoblok, (8) status akhir per channel.

## STATUS TERBARU v75 (16 Nov, chat v29) <- Menggantikan v74 untuk posisi terakhir.
- TERBUKTI (output Mac): tes_lokal.sh tes 7 URL baru, 7 OK 0 gagal, 431 dilewati (masih baru), 13 stream OK berstatus DRM. Playlist 11858. Aman tetap 41 dari 253 (35 lolos lokal + 6 belum dites). Status lama (13-14 Nov) belum dites ulang; tes ulang penuh = bash tes_lokal.sh semua (438 kandidat), jangan lewat tethering (kuota).
- Tes segment Indosiar (curl -v) tidak menyimpulkan: segment terbaru kosong, tidak ada bukti baru. Dugaan header (v73) gugur, salah label Moji TV (v72) gugur; Indosiar tampil hitam 403/404 di STB, sebab belum diketahui.
- TERBUKTI (user): iNews salah channel (Arab), Trans TV salah channel (drama Vision+), ANTV jalan, SCTV mati. ANTV butuh Referer visionplus.id (curl 403 tanpa, 200 dengan).
- R3a BELUM dimulai: STB belum tersambung ke Mac. Rencana: Mac dan STB di hotspot iPhone, Wireless debugging STB, adb mdns services dan adb devices -l, lalu pm list packages -3, cek asal dan lisensi sebelum ambil URL playlist.
- Rencana ganti player TiviMate ke Kepler Player (belum dilakukan). Tes Kepler wajib: Referer (ANTV), header DENSGO, satu channel DRM.
- Antrian revive (urut): (1) adb sambung ke STB, (2) daftar app pihak ketiga dan app IPTV penjual, (3) ambil sumber link hanya kalau asal dan lisensi aman, (4) tes ulang folder 01-15, (5) cabut Indosiar, Trans TV, iNews dari folder utama, (6) cari link SCTV, Indosiar, Trans TV, iNews, (7) tes Kepler, (8) 9 TUNGGU_STB sisa, (9) VPN geoblok, (10) status akhir per channel.

## STATUS TERBARU v76 (16 Nov, chat v30) <- Menggantikan v75 untuk posisi terakhir.
- TERBUKTI (isi zip): zip 14:06 WIB, pembuka berjudul v60 tapi isi POSISI v75 = STATUS v75, keys.sh disebut PETA_FILE tapi tidak ada di zip, out/ tidak ikut zip (by design).
- Aman tetap 41 dari 253. R3a dimulai: cek adb di Mac, adb mdns services, adb devices -l.

## STATUS TERBARU v77 (16 Nov, chat v30) <- Menggantikan v76 untuk posisi terakhir.
- TERBUKTI (output Mac): adb 1.0.41 terpasang di /opt/homebrew/share/android-commandlinetools/platform-tools, adb mdns services kosong, adb devices kosong. STB belum terlihat. Berikutnya: cari IP STB di subnet hotspot, lalu adb connect.

## STATUS TERBARU v78 (16 Nov, chat v30) <- Menggantikan v77 untuk posisi terakhir.
- DUGAAN (pesan user typo): IP STB 172.20.10.10, port 42139. Mencoba adb connect.

## STATUS TERBARU v79 (16 Nov, chat v30) <- Menggantikan v78 untuk posisi terakhir.
- TERBUKTI (output Mac): adb connect 172.20.10.10:42139 berhasil, STB B866F_V1_1 (product oppen) tersambung. R3a jalan: daftar app pihak ketiga (pm list packages -3), versi Android.

## STATUS TERBARU v80 (16 Nov, chat v30) <- Menggantikan v79 untuk posisi terakhir.
- TERBUKTI (output Mac): STB Android 14. App pihak ketiga: aktv (com.aktv.jo), gvision tv v3 (bayustecu.gvision.v3), TiviMate (ar.tvplayer.tv), stremio, tvbrowser, magisk, protonvpn, tizentube, localsend, powermenu, vortex (com.fornax.vortex). Magisk terpasang (root belum dites, DUGAAN). Berikutnya: dumpsys asal dua app IPTV penjual, belum ambil link.

## STATUS TERBARU v82 (16 Nov, chat v30) <- Menggantikan v81 untuk posisi terakhir.
- User minta ekstrak playlist m3u dari aktv dan gvision tv v3. Lisensi belum terjawab, user menganggap layanannya miliknya. Batas: hanya baca file yang terbuka di STB, tanpa membongkar enkripsi atau proteksi app. Langkah 1: find m3u di /sdcard dan lihat folder data eksternal kedua app.

## STATUS TERBARU v83 (16 Nov, chat v30) <- Menggantikan v82 untuk posisi terakhir.
- TERBUKTI (output Mac): tidak ada m3u di /sdcard, aktv tanpa folder data eksternal, gvision files kosong. User menyatakan kedua app dibayar sendiri (klaim user, belum diverifikasi). Langkah: su -c id (tes root) dan ls /data/data kedua app. PERINGATAN: URL playlist berbayar bisa berisi kredensial; jangan tulis ke handoff, log, atau file yang naik ke GitHub Pages publik.

## STATUS TERBARU v84 (16 Nov, chat v30) <- Menggantikan v83 untuk posisi terakhir.
- TERBUKTI (output Mac): adb shell punya root (su uid=0, Magisk). Folder privat aktv (com.aktv.jo) dan gvision (bayustecu.gvision.v3) punya files, shared_prefs, cache. Langkah: daftar nama dan ukuran file saja. Isi file dan URL tidak boleh masuk handoff atau log.

## STATUS TERBARU v85 (16 Nov, chat v30) <- Menggantikan v84 untuk posisi terakhir.
- TERBUKTI (output Mac): listing terpotong cache gambar gvision. gvision cache/HttpClient punya 2 respons tersimpan (57763 dan 58799 byte, DUGAAN data channel/API). files dan shared_prefs kedua app belum terlihat. Langkah: salin files, shared_prefs, HttpClient ke ~/iptv_stb_privat (di luar folder proyek, jangan ikut zip atau GitHub). Isi dan URL tidak ditulis ke handoff atau log.

## STATUS TERBARU v86 (16 Nov, chat v30) <- Menggantikan v85 untuk posisi terakhir.
- TERBUKTI (output Mac): cp ke /sdcard/tmp_* gagal Permission denied, 0 file ter-pull. DUGAAN kuat: quoting, adb shell memecah rangkaian di titik koma sehingga cp jalan bukan sebagai root. Perbaikan: adb shell "su -c '...'" (kutip ganda di luar, tunggal di dalam). Aturan untuk perintah root berikutnya.

## STATUS TERBARU v87 (16 Nov, chat v30) <- Menggantikan v86 untuk posisi terakhir.
- TERBUKTI (output Mac): salinan ke ~/iptv_stb_privat berhasil (quoting su terbukti). gvision: HttpClient 2 respons (57763 dan 58799 byte), Favorite-1.json 8 byte, shared_prefs 532 byte. aktv: Favorite.json 15 byte, shared_prefs 1411 byte, tanpa cache respons. Langkah: baca struktur .1 gvision dengan URL dan query disamarkan. Isi dan URL asli tidak ditulis ke handoff atau log.

## STATUS TERBARU v87 (16 Nov, chat v30) <- Menggantikan v86 untuk posisi terakhir.
- TERBUKTI (output Mac): salinan ke ~/iptv_stb_privat berhasil (quoting su terbukti). gvision: HttpClient 2 respons (57763 dan 58799 byte), Favorite-1.json 8 byte, shared_prefs 532 byte. aktv: Favorite.json 15 byte, shared_prefs 1411 byte, tanpa cache respons. Langkah: baca struktur .1 gvision dengan URL dan query disamarkan. Isi dan URL asli tidak ditulis ke handoff atau log.

## STATUS TERBARU v88 (16 Nov, chat v30) <- Menggantikan v87 untuk posisi terakhir.
- TERBUKTI (output Mac): respons gvision di HttpClient = HTML gzip (290 KB dan 337 KB terbuka) dari host liveloveyou.my.id, diperbarui harian, bukan M3U. sed error karena locale (perlu LC_ALL=C). aktv punya kunci SOURCES_PLAYLIST di shared_prefs. DUGAAN: layanan reseller tidak resmi (host .my.id pribadi, sideload). Hasil ekstraksi hanya lokal di ~/iptv_stb_privat, tidak boleh masuk playlist publik GitHub Pages. Path hash di URL = DUGAAN token akses, jangan ditulis ulang.

## STATUS TERBARU v90 (16 Nov, chat v30) <- Menggantikan v89 untuk posisi terakhir.
- Keputusan user: playlist dari app aktv dan gvision tv v3 dimasukkan utuh ke TiviMate sebagai playlist tambahan (bukan dicocokkan ke 253 dulu). Caranya: salinan lokal di ~/iptv_stb_privat/serve dilayani http.server dari Mac di hotspot, TiviMate tambah playlist via URL. Angka aman tetap 41 dari 253. URL sumber tidak ditulis di handoff atau log.

## STATUS TERBARU v91 (16 Nov, chat v30) <- Menggantikan v90 untuk posisi terakhir.
- PAUSE (HP iPhone dan STB mati). TERBUKTI: import playlist aktv dan gvision ke TiviMate BELUM dilakukan. adb ke STB terputus. Folder ~/iptv_stb_privat/serve berisi salinan lokal, di luar zip.
- Daftar kerja tanpa STB (urut): (1) cocokkan M3U gvision 780 entri ke 227 channel belum aman (offline), (2) tes link kandidat dengan header benar, (3) cabut Indosiar, Trans TV, iNews dari folder utama sebagai BELUM, (4) cari link SCTV, Indosiar, Trans TV, iNews via web dengan Referer, (5) tes ulang folder 01-15 lewat bash tes_lokal.sh semua (bukan lewat tethering), (6) status akhir per channel.
- Butuh STB, ditunda: import ke TiviMate (gvision dan aktv via http.server Mac), tes Kepler, 10 TUNGGU_STB, cek identitas iNews dan Trans TV dan Indosiar. Aman tetap 41 dari 253.

## STATUS TERBARU v92 (16 Nov, chat v30) <- Menggantikan v91 untuk posisi terakhir.
- TERBUKTI (output Mac): pencocokan nama persis M3U gvision (780 entri) ke 227 channel belum aman = 13 cocok: TVRI Sport, Kids TV (2 slot), Mentari TV, Ajwa TV, Ashiil TV, Biznet Kids, My Kidz, Naajiya TV, Mythbusters, PBS Nature, HBO Hits, Lifetime. Negara belum dicek. Risiko salah negara: Mythbusters, PBS Nature, HBO Hits, Lifetime, Kids TV. Kandidat dan URL di ~/iptv_stb_privat/kandidat_gvision.csv, di luar zip. Langkah: tes_kandidat_gvision.py (header dari playlist, DRM ditandai butuh STB).

## STATUS TERBARU v93 (16 Nov, chat v30) <- Menggantikan v92 untuk posisi terakhir.
- TERBUKTI (output Mac): paket catatan v90-v92 masuk (grep=3). Tes 13 kandidat gvision: HIDUP_LOKAL = TVRI Sport, Ashiil TV, Naajiya TV, Lifetime (2), Kids TV (2); HTTP_500 = Mentari TV (2), Ajwa TV; DRM_BUTUH_STB = Mythbusters, PBS Nature; TIDAK_DITEMUKAN = Biznet Kids, My Kidz, HBO Hits (2). DUGAAN: TIDAK_DITEMUKAN akibat bug skrip pencocokan (melewati #EXTINF berikutnya, entri tanpa URL ikut mengambil URL channel di bawahnya).
- Batas atas: 6 slot (TVRI Sport, Kids TV utama, Kids TV likely_dead, Ashiil TV, Naajiya TV, Lifetime) = maksimal 47 dari 253 kalau identitas terbukti. Lolos lokal BUKAN bukti identitas. Langkah: identitas_kandidat.py (metadata, frame ffmpeg bila ada). Hasil di ~/iptv_stb_privat, URL tidak ditulis.

## STATUS TERBARU v94 (16 Nov, chat v30) <- Menggantikan v93 untuk posisi terakhir.
- TERBUKTI (output Mac): identitas_kandidat.py jalan, ffmpeg ada, 9 baris kandidat (5 channel unik) menghasilkan frame di ~/iptv_stb_privat. Lifetime dan Kids TV: tvg-id berakhiran .id, host proxy-v.rctiplus.id dengan Referer (jalur Vision+ Indonesia). DUGAAN: feed Indonesia, bukan versi Amerika untuk slot America; belum dimasukkan. Ashiil TV dan Naajiya TV: host flv.intechmedia.net. TVRI Sport: gvisiontv2.channell.my.id, group Nasional, tanpa tvg-id.
- Cek 3 TIDAK_DITEMUKAN belum menyimpulkan (bug gue: perbandingan nama peka huruf besar, nama di M3U huruf besar). Diulang tanpa membedakan huruf. Berikutnya: user menyeret 5 frame ke chat untuk cek identitas visual.

## STATUS TERBARU v95 (16 Nov, chat v30) <- Menggantikan v94 untuk posisi terakhir.
- TERBUKTI (user): TVRI Sport, Ashiil TV, Naajiya TV, Kids TV, Lifetime ada channelnya (frame dilihat user, tidak diupload ke chat). Lifetime dan Kids TV = jalur Vision+ .id; user tetap menerima, Lifetime ke slot America.
- TERBUKTI (output Mac): Biznet Kids, My Kidz, HBO Hits TIDAK_DITEMUKAN karena URL dikomentari di M3U sumber (#http, ###http, ##http); HBO Hits entri kedua DRM Cubmu. Bukan bug skrip. Biznet Kids punya URL host Biznet (dikomentari) yang bisa dites terpisah.
- Apply R6: 5 channel ke data/extra/links_user.m3u dan data/refill_pick.json (folder sports, islam x2, kids, america). Backup di _arsip/out_sebelum_gvision. Lalu bash tes_lokal.sh dan revive_status.py. PERINGATAN: URL TVRI Sport = relay channell.my.id (token mungkin, DUGAAN), cek sebelum upload GitHub publik.
- Sisa: Mentari TV dan Ajwa TV HTTP_500 (tes ulang), Mythbusters dan PBS Nature DRM (STB).

## STATUS TERBARU v96 (16 Nov, chat v30) <- Menggantikan v95 untuk posisi terakhir.
- TERBUKTI (output Mac): apply R6 sukses. Playlist 11862. 5 channel (TVRI Sport, Ashiil TV, Naajiya TV, Kids TV, Lifetime) di folder benar dan lolos tes lokal (5 OK 0 gagal). Aman 47 dari 253 (18,6 persen; lolos lokal 41, belum dites 6), target 228, kurang 181. Sisa: 173 BELUM, 24 slot URL mati, 9 TUNGGU_STB, 15 latam. Backup _arsip/out_sebelum_gvision dan snapshot iptv_1611_1459.
- Arahan user: semua channel tanpa URL (likely dead, utama, radio) dan yang di major file (DUGAAN: major_brands.yml) harus dicarikan URL; target 90 persen. Hitungan jujur: cocok nama persis gvision 13 dari 227; sumber seperti ini saja kemungkinan tidak cukup (DUGAAN).
- Langkah: unduh playlist aktv dari kunci SOURCES_PLAYLIST (salinan lokal, tanpa STB) ke ~/iptv_stb_privat/serve, lalu cocok_sumber.py ke semua sumber lokal (tier persis dan longgar, akhiran tvg-id negara, URL dikomentari dilewati). Antrian berikutnya: major_brands.yml, Biznet Kids host Biznet, Mentari TV dan Ajwa TV HTTP_500, cabut Indosiar Trans TV iNews, cari link web.

## STATUS TERBARU v97 (16 Nov, EXIT chat v30) <- posisi akhir sebelum pindah chat. Menggantikan v96 untuk posisi terakhir.
- TERBUKTI (output Mac): aktv_1.m3u HTTP 200, 190038 byte, 422 EXTINF; dua sumber aktv lain gagal (HTTP 403 dan 404). gvision 16 Nov: 542 entri berURL, 238 dilewati (URL dikomentari atau kosong). gvision 4 Okt: 477 entri, 275 dilewati.
- TERBUKTI (cocok_sumber.py): dari 221 channel belum aman, 28 punya kandidat, BELUM dites dan negara BELUM dicek. Kandidat: SCTV (3 URL), GTV, ANTV, MNCTV, RCTI HD, Trans TV, Trans7 (aktv, id), Mentari TV, Ajwa TV, Fox News Channel, Baywatch, CBeebies, Celestial Movies, GREAT! movies, History (Brazil dan US), Mythbusters (DRM), Nick Jr. (India dan US), Nickelodeon (India dan UK), PBS Nature (DRM), RT, beIN Sports 1.
- DUGAAN: Nick Jr., Nickelodeon, History rawan salah negara (cocok nama setelah tanda kurung dibuang; tvg negara sumber id, sg, tidak tercantum). Trans TV dan ANTV dari proxy rctiplus bisa salah isi seperti sebelumnya.
- Angka: aman 47 dari 253 (18,6 persen), kurang 181. Maksimal teoretis dari 28 kandidat sekitar 75, jadi sumber ini saja tidak cukup untuk 228 (DUGAAN). Perlu major_brands.yml, web, STB, VPN.
- Langkah pertama chat v31: tes 28 kandidat dari ~/iptv_stb_privat/kandidat_semua_sumber.csv (header Referer dan UA dari opsi playlist asli, DRM ditandai butuh STB), cek negara, identitas lewat frame ffmpeg, apply jalur R6. Skrip di zip: tes_kandidat_gvision.py, identitas_kandidat.py, cocok_sumber.py (tes dan identitas perlu disesuaikan untuk tiga sumber).
- Antrian: major_brands.yml, Biznet Kids (URL host Biznet dikomentari di sumber), Mentari TV dan Ajwa TV HTTP_500 (tes ulang), cabut Indosiar Trans TV iNews dari folder utama, cari link SCTV Indosiar Trans TV iNews (curl dengan Referer), tes ulang folder 01-15 (bash tes_lokal.sh semua, bukan tethering), import aktv dan gvision ke TiviMate lewat http.server Mac (belum dilakukan), tes Kepler, 9 TUNGGU_STB, VPN geoblok.

## STATUS TERBARU v98 (16 Nov, chat v31) <- Menggantikan v97 untuk posisi terakhir.
- TERBUKTI (cek paket): zip 16:59 WIB, pembuka v97 = handoff v97. File hilang yang relevan: tidak ada (kandidat_*.csv memang di ~/iptv_stb_privat). Aman 47 dari 253 (18,6 persen), kurang 181.
- Langkah: tes_kandidat_semua.py menguji 28 kandidat dari kandidat_semua_sumber.csv dengan header dari playlist sumber; hasil di ~/iptv_stb_privat/tes_kandidat_semua.csv. Belum ada perubahan playlist.

## STATUS TERBARU v99 (16 Nov, chat v31) <- Menggantikan v98 untuk posisi terakhir.
- TERBUKTI (output Mac): tes 28 kandidat. Lolos lokal 18 slot: GTV x2, ANTV x2, RCTI HD x2, MNCTV, Trans7 (aktv, id), Fox News (us), CBeebies (uk), Celestial Movies, GREAT! movies, History x2, Nick Jr x2, RT x2. Gagal: SCTV (BUKAN_HLS dan URLError), Mentari TV dan Ajwa TV (HTTP_500), Baywatch dan Nickelodeon x2 (HTTP_404), beIN Sports 1 (URLError), Trans TV (tidak ditemukan di skrip tes). DRM: Mythbusters, PBS Nature.
- DUGAAN: History (Brazil) dan Nick Jr (India) memakai feed negara lain (us, id, sg). Feed Indonesia lewat proxy rctiplus bisa salah isi. Belum ada yang masuk playlist. Aman tetap 47 dari 253.
- Langkah: tes_identitas_semua.py, 1 frame per URL HIDUP_LOKAL, sheet.jpg di ~/iptv_stb_privat/fr2 untuk dicek visual.

## STATUS TERBARU v100 (16 Nov, chat v31) <- Menggantikan v99 untuk posisi terakhir.
- TERBUKTI (output Mac): frame identitas 11 dari 15 URL berhasil. Gagal: GTV, MNCTV, RCTI HD (tanpa pesan, DUGAAN timeout 40 detik) dan GREAT! movies (ffmpeg menolak ekstensi segmen). Hampir semua URL lewat host proxy Vision+ Indonesia, kecuali History gvision. DUGAAN: feed Indonesia untuk channel asing, identitas menunggu frame dilihat. Aman tetap 47 dari 253.
- Langkah: ulang 4 frame gagal (timeout 90 detik, ekstensi segmen dilonggarkan) di fr3/sheet.jpg, lalu user menyeret fr2/sheet.jpg dan fr3/sheet.jpg ke chat.

## STATUS TERBARU v101 (16 Nov, chat v31) <- Menggantikan v100 untuk posisi terakhir.
- TERBUKTI (output Mac): ulang frame berhasil untuk GTV, MNCTV, RCTI HD, GREAT! movies (fr3/sheet.jpg). Total 15 URL lolos lokal punya frame (fr2 11, fr3 4). sheet.jpg belum dilihat Claude, menunggu user menyeret ke chat. Aman tetap 47 dari 253.
- Langkah: cek identitas dan negara dari frame, lalu apply R6 untuk yang lolos (links_user.m3u dan refill_pick.json, backup, bash tes_lokal.sh, python3 revive_status.py).

## STATUS TERBARU v102 (16 Nov, chat v31) <- Menggantikan v101 untuk posisi terakhir.
- TERBUKTI (user): identitas 15 URL lolos lokal dinyatakan aman semua (lihat frame fr2 dan fr3). Gambar tidak sampai ke Claude, jadi verifikasi identitas oleh user, bukan Claude.
- Apply R6b: 12 channel unik (GTV, ANTV, RCTI HD, MNCTV, Trans7, Fox News, RT, GREAT! movies, History, Nick Jr, CBeebies, Celestial Movies) ke data/extra/links_user.m3u (tvg-id slot draft atau gap) dan Celestial ke data/refill_pick.json. Sumber utama aktv. Backup _arsip/out_sebelum_r6b. Lalu bash tes_lokal.sh dan revive_status.py.
- DUGAAN: slot kembar (variant 720p, 1080p, India, Brazil) mungkin tidak naik terpisah karena URL sama dibuang build. Slot History Brazil dan Nick Jr India memakai feed negara lain, diterima user.

## STATUS TERBARU v103 (16 Nov, chat v31) <- Menggantikan v102 untuk posisi terakhir.
- TERBUKTI (output Mac): apply R6b sukses, 12 entri masuk (11 aktv opsi header 2, GREAT! movies opsi header 0). Playlist 11863. Aman 58 dari 253 (22,9 persen; lolos lokal 51, belum dites 7), kurang 170, target 228. Per kelompok: likely_dead 49/213, utama 7/24, radio 2/16. Naik 11 slot dari 47.
- DUGAAN: dari 6 slot utama yang disasar baru 2 naik (utama 5 jadi 7); TUNGGU_STB masih 9, BELUM 164, BELUM_SLOT_ADA_URL_MATI 22. Slot utama lain kemungkinan nyangkut di TUNGGU_STB atau slot lama belum tergantikan. Backup _arsip/out_sebelum_r6b, snapshot iptv_1611_1913.
- Langkah: cetak status_baru slot target dan 9 TUNGGU_STB dari docs/revive_status_1511.csv (tanpa URL) untuk cari slot yang belum nyambung.

## STATUS TERBARU v104 (16 Nov, chat v31) <- Menggantikan v103 untuk posisi terakhir.
- TERBUKTI (output Mac): 11 slot naik lewat R6b: GTV, GTV 1080p, Fox News, CBeebies x2, GREAT! movies, History US, Nick Jr US, RT x2 (lolos lokal) dan Celestial Movies (belum dites). Belum naik: ANTV, MNCTV, RCTI HD, Trans7 (TUNGGU_STB, slot utama sudah diisi entri DRM/MPD), Trans TV (tidak ada kandidat), ANTV 720p, RCTI 1080p, History Brazil, Nick Jr India, GREAT! romance (BELUM).
- DUGAAN: entri aktv kalah rank dari entri DRM/MPD di slot utama. ANTV 720p dan RCTI 1080p ikut naik kalau ANTV dan RCTI utama hidup (pola GTV 1080p). History Brazil dan Nick Jr India butuh feed regional asli, belum ada.
- Apply R6c: 4 pick (ANTV, MNCTV, RCTI HD, Trans7) ke data/refill_pick.json folder national. Backup _arsip/out_sebelum_r6c.

## STATUS TERBARU v105 (16 Nov, chat v31) <- Menggantikan v104 untuk posisi terakhir.
- TERBUKTI (output Mac): R6c (4 pick national) tidak mengubah angka. Aman tetap 58 dari 253 (22,9 persen), likely_dead 49/213, utama 7/24, radio 2/16. TUNGGU_STB tetap 9. Playlist 11863. Backup _arsip/out_sebelum_r6c.
- TERBUKTI (baca kode revive_status.py): baris aksi TUNGGU_STB dengan URL lama masih di folder 01-15 dan tes lokal bukan gagal langsung berstatus TUNGGU_STB, dicek SEBELUM cabang URL pengganti lolos. Selama entri DRM/MPD lama ada di folder utama, URL pengganti tidak dihitung.
- DUGAAN: ANTV 720p dan RCTI 1080p tetap BELUM karena URL aktv tidak ada di folder utama (kalah grup dari entri iptv-org lama). Diagnosis: cetak entri ANTV, MNCTV, RCTI, Trans7, Trans TV dari out/channels.json (folder, status, host, penanda MINE).

## STATUS TERBARU v106 (16 Nov, chat v31) <- Menggantikan v105 untuk posisi terakhir.
- TERBUKTI (output Mac): ANTV, MNCTV, RCTI HD, Trans7 ada di folder 01, lolos lokal, penanda MINE (URL dari links_user.m3u). Entri lama tidak ada lagi. Trans TV masih entri lama di folder 01. ANTV 720p dan RCTI 1080p di Likely Dead (gagal).
- DUGAAN kuat: URL baru identik dengan url_lama (host proxy-v.rctiplus.id path /live/web/...), jadi cur = entri sama dan cabang TUNGGU_STB menang; vonis tes ketat lama (tanpa Referer) menahan varian 720p dan 1080p.
- Patch revive_status.py: VETTED = URL di data/extra/links_user.m3u; ketat(u) kosong untuk VETTED; cabang TUNGGU_STB tidak berlaku bila u di VETTED. Backup revive_status.py.bak_v106. Trans TV tetap TUNGGU_STB (identitas belum dicek).

## STATUS TERBARU v107 (16 Nov, chat v31) <- Menggantikan v106 untuk posisi terakhir.
- TERBUKTI (output Mac): patch revive_status.py (VETTED) jalan. Aman 64 dari 253 (25,3 persen; lolos lokal 57, belum dites 7), kurang 164. likely_dead 51/213, utama 11/24, radio 2/16. TUNGGU_STB tinggal 5 (Trans TV, HGTV Asia, S4C, Antena 3, La Sexta). Naik: ANTV, ANTV 720p, MNCTV, RCTI HD, RCTI 1080p, Trans7. Backup revive_status.py.bak_v106.
- DUGAAN: varian 720p dan 1080p dihitung aman lewat cocok nama ke slot utama yang sama (pola GTV 1080p).
- Langkah: cocok_komentar.py: semua file playlist di ~/iptv_stb_privat (termasuk .html isi M3U), URL dikomentari ikut, tes paralel dengan header asli untuk semua channel BELUM (tanpa latam). Hasil ~/iptv_stb_privat/tes_komentar.csv. Playlist tidak diubah.

## STATUS TERBARU v108 (16 Nov, chat v31) <- Menggantikan v107 untuk posisi terakhir.
- TERBUKTI (output Mac): cocok_komentar.py: 189 channel BELUM, hanya 22 punya kandidat (31 URL) di aktv dan gvision, URL dikomentari (234 di gvision) tidak menambah yang hidup. Hasil: HIDUP_LOKAL 3 (History dan Nick Jr feed US, id, sg, sama dengan yang sudah dipakai slot US; tidak dihitung untuk slot Brazil dan India), DRM_BUTUH_STB 12 (Cartoon Network US, Discovery US UK India, HBO US, HBO Hits, HGTV US, Mythbusters, Nick Jr India, Nickelodeon India dan UK, PBS Nature), gagal sisanya (HTTP_404 6, URLError 5, timeout 2, BUKAN_HLS 2, HTTP_403 1). Aman tetap 64 dari 253 (25,3 persen), kurang 164.
- DUGAAN: sumber aktv dan gvision habis. Sisa BELUM kebanyakan merek berbayar atau geo-blok; target 228 kemungkinan tidak tercapai dengan sumber publik. Channel tanpa sumber gratis berstatus akhir MATI_PERMANEN dengan alasan.
- Langkah: cari_radio.py: 14 radio_non_hidup dicari ulang di radio-browser (countrycode ID, nama cocok minimal 60 persen), tes audio paralel, hasil ~/iptv_stb_privat/tes_radio.csv. Playlist tidak diubah.

## STATUS TERBARU v109 (16 Nov, chat v31) <- Menggantikan v108 untuk posisi terakhir.
- Permintaan user: tracker sheets untuk revive. Dibuat buat_tracker.py (baca docs/revive_status_1511.csv, tulis docs/tracker_revive.xlsx: tab Ringkasan, Tracker 268 baris, Sumber dan Catatan). Tanpa URL. Tes sandbox: 349 rumus, 0 error. Menjalankan ulang menimpa kolom isian manual (Status akhir, Catatan).
- Aman tetap 64 dari 253 (25,3 persen), kurang 164. Output cari_radio.py (radio) belum diterima; langkah radio masih menunggu.

## STATUS TERBARU v110 (16 Nov malam, EXIT chat v31) <- posisi akhir sebelum pindah chat. Menggantikan v109 untuk posisi terakhir.
- TERBUKTI (output Mac): aman 64 dari 253 (25,3 persen; lolos lokal 57, belum dites 7), kurang 164, target 228. likely_dead 51/213, utama 11/24, radio 2/16. Playlist 11863. R6b (12 channel dari aktv) dan patch VETTED di revive_status.py (backup .bak_v106) menaikkan 47 jadi 64.
- TERBUKTI: aktv dan gvision sudah dicocokkan ke 189 BELUM termasuk URL dikomentari: 22 channel punya kandidat, 0 aman baru, 12 DRM butuh STB. Sumber app habis. Tracker: docs/tracker_revive.xlsx dari buat_tracker.py (menjalankan ulang menimpa kolom isian K dan L).
- TERBUKTI (halaman iptvplayer.stream): hanya browser playlist iptv-org dan Free-TV, tanpa stream sendiri; alat Stream Checker, Playlist Cleaner, Duplicate Remover; promosi Kepler (trial 30 hari, klaim situs). Tidak ada sumber baru. DUGAAN: Free-TV terbaru belum dicocokkan ke semua BELUM.
- Belum diterima: output cari_radio.py (14 radio, hasil ~/iptv_stb_privat/tes_radio.csv).
- Antrian: radio, Free-TV segar plus cocok_komentar.py, Mentari TV dan Ajwa TV (HTTP_500), Biznet Kids, My Kidz, cabut Indosiar Trans TV iNews dari folder utama, link SCTV Indosiar Trans TV iNews, 12 DRM dan 5 TUNGGU_STB di STB, import aktv dan gvision ke TiviMate, Kepler, major_brands.yml, bash tes_lokal.sh semua, VPN geoblok, status akhir semua channel (MATI_PERMANEN pakai alasan).


## STATUS TERBARU v111 (16 Nov malam, chat v32) <- Menggantikan v110 untuk posisi terakhir.
- Apply batch A: 7 radio (Fress FM, Radio AR Bali, Radio Elshinta Bandung, Radio Rodja, Retjo Buntung, SmartRadio, Suara Giri) lewat data/radio_cache.json dan data/vetted_urls.txt (file baru; revive_status.py membacanya, backup revive_status.py.bak_v110), TRT 1 lewat refill_pick.json (europe) dan tes ulang. Hasil hitung revive_status.py: aman 68 dari 253, utama_non_hidup 11/24, radio_non_hidup 5/16, likely_dead 52/213.
- Ditolak (DUGAAN feed beda): Discovery India UK US (Free-TV Italia), History Brazil dan Nick Jr India (host sama dengan versi US). 10 DRM tetap menunggu STB. Radio tanpa kandidat hidup: Media FM Surabaya, Al-Faruq, El Shaddai, Gema Surya, Hang FM, Radio Islam Malang 1 (2 baris).
- Antrian: Mentari TV, Ajwa TV, Biznet Kids, My Kidz, cabut Indosiar Trans TV iNews dan cari link SCTV Indosiar Trans TV iNews, major_brands.yml, tes_lokal.sh semua, STB, VPN, status akhir.
- v111b (patch kedua): revive_status.py (backup .bak_v111) mengecualikan URL VETTED dari vonis URL sama dengan url_lama belum dites. Sebab: tes_lokal.sh tidak menguji URL radio, jadi AR Bali, Elshinta Bandung, Rodja, Retjo Buntung tertahan walau audio HIDUP di cari_radio.py. Hasil: aman 70 dari 253, kurang ke target 228: 158, utama_non_hidup 11/24, radio_non_hidup 7/16, likely_dead 52/213. Audio radio hanya dites Python (belum diputar di TiviMate); identitas dari nama (DUGAAN).
- v111c: Rodja (& 100.1 FM) dan Retjo Buntung 99.4 FM tertahan karena URL pilihan ada di entri cache bernama beda (kemiripan nama di bawah 0,6); URL pilihan ditaruh di entri bernama persis (backup data/radio_cache.json.bak_v111c). Hasil: aman 71 dari 253, kurang ke target 228: 157, utama_non_hidup 11/24, radio_non_hidup 8/16, likely_dead 52/213.
- v111d: Rodja & 100.1 FM tetap BELUM (URL pilihan kembar dengan entri Radio Rodja 756 AM, dibuang build.py sebagai duplikat; playlist 11861). Radio naik 6: Fress FM, AR Bali, Elshinta Bandung, SmartRadio, Suara Giri, Retjo Buntung. Usulan fase F: SUDAH_TERCOVER, menunggu keputusan user. Batch B dimulai: tes 8 channel (SCTV, Indosiar, Trans TV, iNews, Mentari TV, Ajwa TV, Biznet Kids, My Kidz) di semua sumber dengan 6 varian header, hasil di ~/iptv_stb_privat/tes_b.csv, frame di ~/iptv_stb_privat/frame_b. Repo tidak diubah.

## STATUS TERBARU v112 (17 Nov, chat v32)
- Batch B: tes 50 URL untuk 8 channel (6 varian header, ffmpeg frame). Identitas oleh user: BENAR Indosiar (gvision OXY), iNews (gvision VS OS6, rctiplus), SCTV (gvision OXY), Trans TV (aktv, host CNBC Indonesia, Referer detik); SALAH Indosiar HD dhanytv (Moji HD) dan Trans TV rctiplus (drama Vision+). Keempat yang benar dipasang (SCTV, Indosiar, Trans TV dengan tvg-id slot; iNews gap), relay gvision di data/extra/privat_relay.m3u (JANGAN upload GitHub), lainnya di links_user.m3u. URL salah di data/salah_channel.txt, dilawan oleh tandai_salah.py (jalankan ulang setelah bash tes_lokal.sh semua). Backup: snapshot backup.sh.
- Usulan status akhir (menunggu keputusan user di fase F): Biznet Kids MATI_PERMANEN (domain DNS mati di R3a dan tes 17 Nov, tanpa sumber lain); Ajwa TV, Mentari TV, My Kidz TUNGGU_STB (hanya sumber DASH, butuh STB); Rodja & 100.1 FM SUDAH_TERCOVER. Hasil hitung: aman 72 dari 253, kurang ke target 228: 156, utama_non_hidup 12/24, radio_non_hidup 8/16, likely_dead 52/213.
- v112c (17 Nov): Batch C major_brands.yml tidak berguna (katalog promosi arsip, tidak ada kandidat). Sisa 156: geoblok 62 (butuh VPN, user perlu setup dulu, ditunda), 404 37, host mati 31, DNS mati 22, koneksi ditolak 15, lainnya 22 (sebaran dari revive_kerja.csv, agak lama). Jangan pakai mirror i.mjh.nz (dicabut klaim hak cipta). Langkah berikutnya tanpa VPN: cek hasil Trans TV dan iNews, tes ulang folder 01-15, STB, status akhir.

## STATUS TERBARU v112d (17 Nov, chat v33)
- TERBUKTI: Trans TV CNBC gagal tes lokal karena server membalas playlist dalam gzip dan check_local.py tidak membukanya (bukan stream mati, bukan header). Patch: fetch() di check_local.py gunzip bila byte awal 1f8b (backup check_local.py.bak_v112d). iNews sudah masuk lewat Free-TV (live.i-news.tv, folder News), link rctiplus cuma cadangan. Hasil tes ulang dan angka aman: lihat output revive_status.py.
- v112e (17 Nov): 5 baris radio (Al-Faruq, Hang FM, Islam Malang 1 x2, Suara Muslim Surabaya) dulu vonis text/html; probe socket dengan UA VLC TERBUKTI ngalirin audio di semua path. DUGAAN vonis lama karena UA browser. Dipasang lewat radio_cache.json dan vetted_urls.txt dengan path /; (backup .bak_v112e). Identitas lewat icy-name, belum diputar di STB.
- v112f (17 Nov): keputusan user "ikut rekomendasi": 9 channel Latin America (AXN, Cartoon Network, Disney Channel, E! x2, ESPN x2, ESPN 2 x2) MATI_PERMANEN karena hanya ada feed regional audio Spanyol (docs/status_akhir.csv). MTV India 576p dipromosikan ke slot MTV India HD (396p) lewat refill_pick.json (folder america, backup .bak_v112f). Radio 12 dari 16 (Al-Faruq, Hang FM, Suara Muslim identitas belum terbukti, icy-name placeholder). Hasil angka aman: lihat output revive_status.py.
- v112g (17 Nov, chat v33): update_sumber.sh tarik iptv-org 11558 entri dan dhanytv 954 entri (backup data di _arsip/sebelum_update_1711), lalu tes_lokal.sh: aman 82 dari 253, kurang ke target 228: 146. TERBUKTI identitas (user lihat frame, ~/iptv_stb_privat/frame_c): Channel 4, France 2, France 5, ZDFneo, BBC Two HD, semua BENAR, host baru cdn-redge.media (Channel 4 dan BBC Two dulu DIBLOK_403_GEOBLOK, kini lolos).
- v112h (17 Nov): grep semua sumber publik: Ajwa TV, Biznet Kids, My Kidz hanya punya satu URL, tidak ada kandidat baru. Ajwa TV dan Biznet Kids MATI_PERMANEN (docs/status_akhir.csv). My Kidz tetap TUNGGU_STB (hanya terbuka dari jaringan IndiHome). BELUM 158.
- v112i (17 Nov): host aynascope.net mati total (0 dari 8 kombinasi host); aynaott.com hidup. beIN Sports USA, Golf Channel, Fox Business masuk data/vetted_urls.txt (vonis ketat lama menahan URL yang lolos tes lokal); Disney Junior (US) dan Willow pindah ke tvsen5.aynaott.com lewat data/extra/links_user.m3u (backup .bak_v112i). Identitas TERBUKTI (frame): beIN, Golf, Disney Junior, Willow. Fox Business frame gagal, user melaporkan aman. MS NOW dilewati (BEKU). Aman 87 dari 253, kurang 141.
- v112j (17 Nov): tes ulang 75 URL BELUM non-geoblok non-DNS: naik channel: Disney Junior (United States), PBS KQED, Willow. Identitas TERBUKTI benar (user lihat frame). Sisanya tetap mati dari Indonesia (tes 17 Nov). Aman 88 dari 253, kurang 140.
- v112k (17 Nov): hapus cache tes 59 URL geoblok lalu tes_lokal: aman tetap 88 dari 253 (kurang 140). 8 URL geoblok balas EXTM3U dari IP Indonesia lewat vpn_tes.py (CBS Sports Golazo, DUST, MST3K, Overtime, PBS Nature, TVE Internacional America dan Europe, Vevo Hip Hop) tapi tidak lolos tes_lokal (DUGAAN segmen diblok). Frame TERBUKTI benar (user): GB News, La 1, TV5Monde Info, Cinemax Asia, BBC Two HD, CNN HD, HBO Asia SD, Trace Urban, Trace Urban International. Frame gagal (403 tanpa Referer di proxy-v.rctiplus.id, GREAT! movies ditolak ffmpeg), user melaporkan benar: ANTV, Celestial Movies, History US, Nick Jr, RT, GREAT! movies. VPN belum aktif saat tes (IP negara ID). vpn_tes.py diperbarui: cek segmen dan tolak jalan bila IP ID.
- v112l (17 Nov): BELUM non-geoblok dipisah: berbayar (MATI_PERMANEN, alasan dari kategori tes 17 Nov, docs/status_akhir.csv, backup .bak_v112l) dan gratis/FTA 32 (tetap diburu). Ditahan di BELUM karena siaran gratis US/FAST: NBC, NBC West, Fox US West, Laff, Reelz, DAZN F1, MTV India.
- v112m (17 Nov): keputusan user "go latam": sisa Latin America (feed regional audio Spanyol) MATI_PERMANEN di docs/status_akhir.csv (backup .bak_v112m).
- v112n (17 Nov, chat v33): cari_belum.py cocokkan 93 BELUM ke index/dhanytv/gist/links_user, 63 URL dites, hasil docs/cari_belum_1711.csv. Dipasang: BBC One London HD (links_user.m3u, tvg-id slot), Canale 5 HD dan TVE Internacional Europe (tvg_id diisi di draft_esensial.csv: Canale5.it@HD, TVEInternacionalEurope.es@SD). TERBUKTI mekanisme: slot draft dicocokkan lewat tvg_id ke entri iptv-org saja, tvg_id kosong berarti draft tidak ketemu. Aman 93 dari 253, kurang 135. Kembaran Canale 5 [Geo-blocked] dan TVE Europe HD ikut AMAN (DUGAAN URL sama, usulan SUDAH_TERCOVER di fase F). Ditolak (feed negara beda): Cartoon Network, Discovery, ID, NatGeo, TNT, Channel 5, MTV, NatureTime, Polsat, Setanta, Racer, Islam Channel. Ditahan: beIN Sports 1 (kandidat feed Indonesia, slot MENA), arte France (feed Jerman). Antena 3 tanpa slot draft, DUGAAN DASH, tunggu STB. Backup: draft_esensial.csv.bak_v112n, data/extra/links_user.m3u.bak_v112n dan .bak_v112n2. Langkah berikut: VPN UK, python3 vpn_tes.py.
- v112o (18 Nov, chat v33): aman ketat 93 dari 253 (kurang 135), ditambah 5 pengganti feed negara lain (dihitung terpisah, nama jujur): Nick Jr. (Russia), Nickelodeon (France), Nickelodeon (Germany), Sony Channel (Brazil), Sony Movies (United States). Dipasang lewat pasang_pengganti.py (ubah atau tambah baris draft_esensial.csv dengan tvg_id kandidat iptv-org), lalu dicabut selektif oleh sisa_nick_sony.py: Animal Planet, Discovery (Italy dan Czech), HGTV, HBO Czech dibuang atas keputusan user. TERBUKTI: slot draft dicocokkan lewat tvg_id ke entri iptv-org; nama channel di playlist ikut nama kandidat, jadi revive_status tidak melihatnya sebagai aman slot lama. VPN: Windscribe Free, US lolos 26 dari 56 geoblok, GB lolos 19, gabungan 27 (8 satu host turnerlive); Proton Free dan TunnelBear tidak bisa pilih negara; Mullvad opsi berbayar dengan CLI untuk ganti negara otomatis (belum langganan). Frame GB: 12 berhasil dan benar menurut user, 7 gagal (GREAT! romance, Mythbusters, Premier Sports 1 dan 2, Racer Network, BBC One geo, MST3K). selamatkan_vpn.py: 58 MATI_PERMANEN dites ulang dari IP US, 0 URL slot asli hidup, 13 kandidat lolos dari US, 12 juga lolos dari Indonesia (docs/selamatkan_ID.csv), Cartoon Network HD+ 403 dari Indonesia (butuh VPN US), Fox Sports 2 dan TNT Sports 1 lolos tes tapi ffmpeg Invalid data (TUNGGU_STB). FX, HBO, AMC, USA, CNBC, HGTV, Hallmark, Bravo tetap MATI_PERMANEN berbayar. Skrip baru: cari_belum.py, frame_vpn.py, selamatkan_vpn.py, pasang_pengganti.py, sisa_nick_sony.py, frame_pengganti.py. Hasil: docs/cari_belum_1711.csv, docs/vpn_hasil_US.csv, docs/vpn_hasil_GB.csv, docs/selamatkan_US.csv, docs/selamatkan_ID.csv. Frame di ~/iptv_stb_privat (frame_GB, frame_US, frame_selamat_US, frame_pengganti, di luar zip). Backup: draft_esensial.csv.bak_v112n, .bak_v112o, .bak_v112o2; data/extra/links_user.m3u.bak_v112n dan .bak_v112n2. Pelajaran baru: (11) pengambilan frame ffmpeg butuh -allowed_extensions ALL dan Referer dari EXTVLCOPT; (12) kandidat lolos dari IP VPN belum tentu geoblok, tes ulang dari Indonesia dulu; (13) kandidat negara lain jangan diberi nama slot lama. Menunggu keputusan user: VPN berbayar permanen di STB atau router (27 channel plus Cartoon Network HD+), dan sesi STB. Dilarang upload GitHub kecuali user minta.
- v112q sampai v112s (21 Nov, chat v33): aman 98 dari 253 (kurang 130). v112q: semua channel belum-aman dimasukkan ke folder utama dengan tanda [MATI], [VPN], [STB], [BELUM] di nama draft_esensial.csv plus daftar pin di rules.yml (semua_ke_folder.py, backup .bak_v112q). TERBUKTI: build.py place() melempar entri gagal tes ke Archive Likely Dead kecuali namanya ada di pin. v112r: masukkan_sisa.py menaruh 65 channel yang entri sumbernya hilang dari index.m3u lewat entri extra di data/extra/links_user.m3u plus baris gaps di rules.yml (backup .bak_v112r); 157 dari 170 belum-aman kini di folder utama. 13 belum masuk: 30A Golf Kingdom, DAZN F1, F1 Channel, Fight Network, Hallmark Channel, NFL Network, One Golf, Overtime, Racer Network, Sky Sport Golf, Select, Tennis, TVE Internacional America (720p). v112s: nama folder English tanpa nomor dan urutan baru (Documentary & Science setelah Movies & Series) lewat ubah_folder.py (rules.yml.bak_v112s); nomor di group-title sudah dibuang build.py baris 131 sejak awal, nomor hanya muncul di Excel lama. naikkan_major.py menaikkan merek major dari Archive: hanya Cartoon Network Asia Thailand dan Rai 2 HD; Rai 2 belum muncul di folder utama (DUGAAN dibuang sebagai duplikat URL); Latin America dikecualikan sesuai keputusan user. Excel channel_major.xlsx dibuat dari data_excel.zip oleh buat_excel_major.py: 584 channel di folder utama (319 hidup, 84 mati, 44 belum final, 30 VPN, 2 STB), 176 merek major (103 ada dan hidup, 25 ada tidak hidup, 48 belum ada); 4 merek hanya punya feed Latam (Warner TV, TLC, Cartoonito, Golf Channel), menunggu keputusan user. Menunggu keputusan user: langganan VPN dan tes Windscribe di STB (blok serve_test sudah dikirim), dan upload GitHub (links_user.m3u dan rules.yml memuat entri dari app, jangan diupload). Catatan: blok status_akhir v112p (24 MATI_PERMANEN baru, backup docs/status_akhir.csv.bak_v112p) belum terkonfirmasi jalan. Backup: draft_esensial.csv .bak_v112q .bak_v112r .bak_v112s, rules.yml .bak_v112q .bak_v112r .bak_v112s.
