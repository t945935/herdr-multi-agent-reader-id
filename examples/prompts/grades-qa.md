# QA: sistem nilai siswa

Baca antarmuka `examples/grades.py` serta kasus nilai yang ada di `tests/test_contracts.py`. Periksa kontrak nilai secara independen. Jangan ubah kode, menghapus tes lama, membaca penilaian diri Developer, atau memulai agen lain.

Hanya tambahkan atau ubah `tests/test_grades_review.py`; tulis laporan ke `reports/grade-qa.md`. Periksa tiga mata pelajaran, batas 0/100/60, bool/NaN/string, data kosong, nama, peringkat seri 1/1/3, presisi tanpa pembulatan, dan imutabilitas masukan.

Gunakan pytest. Jika tes yang ada sudah mencakup kasus secara memadai, jelaskan kriterianya dan tambahkan hanya cakupan baru yang bernilai; jangan menduplikasi tes identik. Jangan menguji FastAPI, SQLite, atau CRUD situs web—tugas ini khusus sistem nilai siswa.

Jalankan tes dan simpan perintah aktual, kode keluar, temuan, serta yang belum dijalankan. Sertakan `task_id` dan `completion_path` yang ditambahkan Manager di kuitansi; daftarkan berkas laporan dan tes yang dibuat dalam `artifacts`.
