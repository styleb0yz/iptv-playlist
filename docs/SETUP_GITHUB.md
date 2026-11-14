# Setup GitHub (Batch 4), sekali saja

Belum pernah dijalankan; workflow ini baru tervalidasi sintaks YAML dan tes lokal. Jalankan berurutan, kabari hasil tiap langkah.

1. Buat akun/login github.com -> New repository -> nama `iptv-playlist` -> **Public** -> Create.
2. Upload file (Add file > Upload files): semua isi folder `iptv` KECUALI `venv/`, `out/`, `_arsip/`, `update.yml`. Pastikan `data/` ikut, termasuk `data/status_lokal.json` dan `data/extra/`. Commit.
3. Add file > Create new file, nama `.github/workflows/update.yml` (ketik path itu persis), tempel isi `update.yml`, Commit.
4. Settings > Pages > Build and deployment > Source: **GitHub Actions**.
5. Settings > Actions > General > Workflow permissions: **Read and write permissions** > Save.
6. Actions > update-playlist > Run workflow. Tunggu (bisa puluhan menit, belum diketahui).
7. Kalau hijau: buka `https://USERNAME.github.io/iptv-playlist/playlist.m3u` di browser. Masukkan URL itu ke TiviMate.
8. Kalau merah: kirim nama langkah yang gagal + 20 baris terakhir lognya.

Perawatan harian setelah ini: lihat `README.md`. Tes stream Indonesia tetap dari Mac, lalu upload `data/status_lokal.json` baru ke repo (Add file > Upload files, timpa).
