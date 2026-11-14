## Catatan Indonesia (ditulis manual setelah build 13 Nov 2026, status_lokal 252 OK / 416)
Folder 01-02: 21 channel, semuanya lolos tes lokal, kecuali yang tercatat di bawah. Catatan ini ditulis tangan: build.py menimpa laporan.md tiap dijalankan, jadi salin lagi kalau perlu.

Draft Indonesia yang belum punya kandidat lolos, sekarang ada di folder 70 (Archive · Likely Dead):
- SCTV: IP 202.150.172.59 timeout, SCTV HD (dens.tv) 404, DASH indihometv gagal.
- Trans TV, Trans7: 119.82.250.109 403, varian detik/cnbcindonesia hanya 159 byte.
- TVRI Sport: IP 202.150.172.59 timeout.
- RRI Net: 404.
- BeritaSatu: entri iptv-org gagal DNS. "Berita Satu (DensTV)" di dhanytv lolos, tapi URL-nya /btv/ dan tvg-id-nya BTV.id, jadi dihitung duplikat BTV, bukan BeritaSatu. Isi streamnya belum diverifikasi.
- Al-Iman TV, Surau TV: 404. Mentari TV: belum dicek ulang di laporan ini.

Koreksi handoff v3: GTV TIDAK termasuk yang gagal. "GTV (Indonesia) HD" menang lewat proxy-v.rctiplus.id/gtv (lolos). Yang gagal hanya varian IP 202.150.172.59 dan malingtv.workers.dev. MNCTV juga lolos lewat proxy-v.rctiplus.id.
Lolos tes bukan jaminan jalan di TiviMate (header khusus belum diuji).
