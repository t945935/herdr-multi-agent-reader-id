# Developer: kontrak nilai siswa

Baca kasus nilai di `examples/grades.py` serta `tests/test_contracts.py` terlebih dahulu. Ubah hanya `examples/grades.py`; jangan mengubah tes yang ada, kode situs web, atau memulai agen lain.

Kontrak: tepat tiga mata pelajaran—English, History, dan Mathematics. Nilai adalah `int`/`float` berhingga; tolak bool, string, mata pelajaran hilang atau tambahan, dan nilai di luar 0–100. Rata-rata 60 dinyatakan lulus. Daftar siswa kosong menghasilkan daftar kosong. Urutkan berdasarkan total yang belum dibulatkan menggunakan peringkat kompetisi dan pertahankan urutan masukan saat seri; jangan mutasi data masukan.

Pertahankan antarmuka `calculate_total`, `calculate_average`, `get_grade`, dan `rank_students`. Periksa kontrak dan perbaiki hanya jika perlu. Jika implementasi sudah sesuai, pertahankan kode dan laporkan pemeriksaan alih-alih menulis ulang hanya demi membuat diff.

Jalankan `.venv/bin/python -m pytest -q tests/test_contracts.py -k 'ranking or scores'`. Catat perintah aktual, kode keluar, berkas yang diubah, dan masalah tersisa ke `reports/grade-developer.md`. Gunakan `task_id` dan `completion_path` yang ditambahkan Manager untuk kuitansi penyelesaian.
