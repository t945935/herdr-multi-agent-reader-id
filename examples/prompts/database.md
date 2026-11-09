# Database

Ubah hanya `examples/task_manager/db.py`. Sediakan `init_db`, `get_tasks`, `get_task`, `create_task`, `update_task`, dan `delete_task`. Tes dapat mengganti `DB_PATH`; selalu tutup koneksi, gunakan transaksi untuk penulisan, dan parametrisasi nilai SQL. Nama kolom dinamis hanya boleh diambil dari daftar izin tetap. Kembalikan `None`/`False` jika data tidak ditemukan; jangan menyamarkan pengecualian basis data sebagai daftar kosong.
