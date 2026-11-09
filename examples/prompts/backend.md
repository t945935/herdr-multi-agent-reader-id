# Backend

Ubah hanya `examples/task_manager/main.py`. Inisialisasi tabel melalui lifespan FastAPI; tolak kolom tak dikenal dan konversi tipe otomatis. Keberhasilan POST adalah 201, PATCH 200, DELETE 204; data tidak ditemukan menghasilkan 404 dan masukan tidak valid 422. Kolom PATCH yang tidak dikirim mempertahankan nilainya; `null` eksplisit ditolak; deskripsi boleh dikosongkan. Jangan ubah berkas milik Database.
