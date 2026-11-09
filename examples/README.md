# Paket contoh yang dapat dijalankan

Jalankan semua perintah dari direktori akar proyek hasil ekstraksi. Impor modul melalui `examples.*`.

Prompt penilaian siswa ada di `prompts/grades-developer.md` dan `prompts/grades-qa.md`; `prompts/qa.md` khusus situs web. Tetapkan pekerjaan di salinan latihan Anda agar versi acuan tetap utuh.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -q tests
.venv/bin/python -m examples.pipeline
```

| Bab | Titik masuk | Fokus penerimaan |
| --- | --- | --- |
| 1 | `calculator.py` | Aritmetika, pembagian dengan nol, dan tipe |
| 2 | `grades.py` | Batas nilai, mata pelajaran hilang, dan seri kompetisi |
| 3 | `../scripts/probe_herdr.py --live` | Jalankan, baca, tunggu, dan bersihkan panel shell baru |
| 4 | `../scripts/team.py` | Penugasan bertahap, ID tugas unik, penerimaan artefak |
| 5 | `prompts/reviewer-a.md`, `reviewer-b.md` | Tinjauan independen dan keputusan Manager |
| 6 | `handoff.py` | Keberadaan berkas, cakupan proyek, SHA-256 |
| 7 | `task_manager/` | CRUD, validasi, halaman statis, persistensi setelah restart |
| 8 | `research.py` | Klaim, sumber, kutipan, dan ketidakpastian |
| 9 | `pipeline.py` | Kode keluar, waktu tunggu, penerimaan, berhenti saat gagal |
| 10 | `queue.py` | Deduplikasi, lease, pemulihan, dead letter, konkurensi |

Jalankan situs web:

```bash
.venv/bin/python -m uvicorn examples.task_manager.main:app --host 0.0.0.0 --port 8000
```

Di WSL, buka `http://localhost:8000/` di browser Windows. Data latihan disimpan baku di `examples/data/tasks.db`; tes otomatis memakai direktori sementara dan tidak menyentuh berkas itu.

Antrean latar adalah contoh komputasi murni yang terbatas dan tidak memanggil model berbayar. Penugasan model aktual dinyatakan secara eksplisit di `scripts/team.py`; pasang dan login ke CLI terkait terlebih dahulu.
