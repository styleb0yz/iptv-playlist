# PETA FILE IPTV (baca ini kalau bingung mana yang dipakai)

## Aktif (jangan dipindah atau dihapus)
- ~/Downloads/iptv : proyek, sumber kebenaran. Tidak ada venv, python3 sistem cukup.
- ~/Downloads/iptv_kirim_DDMM_HHMM.zip : zip aktif untuk chat baru. Hanya satu; yang lama dipindah otomatis ke backup.

## Backup (~/IPTV_BACKUP, tidak pernah dihapus otomatis)
- snapshot/ : salinan proyek bertanggal (dibuat tiap kirim.sh atau backup.sh)
- zip/ : semua zip lama, termasuk iptv_kirim_v5_PULIHAN.zip
- trash-rescue/ : salinan item IPTV dari Trash (folder iptv lama, zip v3 sampai v7, tivimate.apk)
- arsip-downloads/ : iptv-upload dan update.yml.untuk-github (basi)
- ~/Downloads/iptv/_arsip : backup per patch file proyek

## Bukan IPTV (jangan disentuh)
- ~/tv (proyek CleanYourTV; keys.sh rahasia, jangan masuk zip atau GitHub)
- ~/Downloads/New Folder With Items (DUGAAN aset CleanYourTV)
- ~/Downloads/ARSIP (arsip lama buatan user)
- ~/epg (clone iptv-org/epg)

## Aturan baku
1. Zip untuk chat baru hanya dibuat dengan: bash ~/Downloads/iptv/kirim.sh
2. Jangan unzip lewat Finder. Unzip ke /tmp, lalu salin file satu per satu.
3. Jangan unzip -o ke ~/Downloads/iptv (menimpa status_lokal.json dan build.py).
4. build.py Mac punya modifikasi sendiri: jangan ditimpa dengan build.py dari zip.
5. Sebelum menghapus apa pun di Downloads: cek peta ini dan pastikan ada snapshot terbaru.
6. Trash macOS kosong otomatis 30 hari: jangan menaruh file penting di Trash.
7. Jangan upload docs/ ke repo publik (berisi IP LAN dan jalur lokal).

## Restore dari snapshot
Lihat daftar: ls ~/IPTV_BACKUP/snapshot
Salin ke tempat uji dulu: rsync -a ~/IPTV_BACKUP/snapshot/iptv_XXXX_XXXX/ /tmp/iptv_uji/

## Pesan pembuka
- ~/Downloads/iptv/PESAN_PEMBUKA.txt : salinan pesan pembuka untuk chat baru (versi v5). Ikut zip dan snapshot. Salinan lama di ~/IPTV_BACKUP/PESAN_PEMBUKA.txt dibiarkan. Kalau handoff ganti versi, perbarui file ini.
