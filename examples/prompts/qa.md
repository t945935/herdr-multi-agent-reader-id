# QA

Ubah hanya `tests/`. Tes harus mengikuti persyaratan, bukan melemahkan spesifikasi agar lolos. Isolasi SQLite menggunakan `tmp_path` dan jalankan `TestClient` melalui lifespan aplikasi. Cakup CRUD, tipe, null, kolom tak dikenal, data yang hilang, dan persistensi setelah restart. Jalankan tes serta catat perintah, versi, kode keluar, dan ringkasan kegagalan.
