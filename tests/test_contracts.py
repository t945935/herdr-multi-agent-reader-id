import copy
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor

import pytest

from examples import calculator as calc, grades
from examples.handoff import validate as validate_handoff
from examples.pipeline import run
from examples.queue import Queue, work_once
from examples.research import render, validate


def scores(value):
    return {subject: value for subject in grades.SUBJECTS}


def test_operasi_kalkulator():
    assert [calc.add(2, 3), calc.subtract(2, 3), calc.multiply(2, 3), calc.divide(2, 4)] == [5, -1, 6, .5]
    with pytest.raises(ZeroDivisionError):
        calc.divide(1, 0)


@pytest.mark.parametrize("value", [True, "5", None, float("nan"), float("inf")])
def test_kalkulator_menolak_masukan_tidak_valid(value):
    with pytest.raises(ValueError):
        calc.add(value, 1)


def test_pemeringkatan_kompetisi_stabil_tanpa_mutasi():
    students = [{"name": name, "scores": scores(value)} for name, value in [("Andi", 80), ("Budi", 80), ("Citra", 59)]]
    before = copy.deepcopy(students)
    rows = grades.rank_students(students)
    assert [r["rank"] for r in rows] == [1, 1, 3]
    assert [r["name"] for r in rows] == ["Andi", "Budi", "Citra"]
    assert rows[0]["total"] == 240
    assert rows[2]["grade"] == "Tidak lulus"
    assert students == before
    assert grades.rank_students([]) == []
    assert grades.get_grade(60) == "Lulus"


@pytest.mark.parametrize("bad", [None, {}, {"English": 90}, {**scores(90), "Art": 80}, scores(True), scores(-1), scores(101), scores(float("nan")), scores("90")])
def test_validasi_nilai(bad):
    with pytest.raises(ValueError):
        grades.calculate_total(bad)


def test_pemeringkatan_tanpa_pembulatan():
    rows = grades.rank_students([{"name": "Andi", "scores": scores(80.001)}, {"name": "Budi", "scores": scores(80.002)}])
    assert [r["rank"] for r in rows] == [1, 2]
    assert rows[0]["name"] == "Budi"


def test_validasi_hash_dan_jalur_serah_terima(tmp_path):
    artifact = tmp_path / "result.txt"
    artifact.write_text("accepted")
    record = {"task_id": "T1", "from": "developer", "to": "qa", "completed": "implementasi", "next": "uji",
              "artifacts": [{"path": "result.txt", "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest()}]}
    assert validate_handoff(record, tmp_path)
    artifact.write_text("changed")
    with pytest.raises(ValueError):
        validate_handoff(record, tmp_path)
    record["artifacts"][0]["path"] = "../outside"
    with pytest.raises(ValueError):
        validate_handoff(record, tmp_path)


def test_klaim_didukung_memerlukan_bukti_valid():
    data = {"question": "Pertanyaan riset", "sources": [{"id": "S1", "title": "Dokumentasi utama", "url": "https://herdr.dev/", "accessed": "2026-11-06", "kind": "official"}],
            "claims": [{"text": "Klaim yang diuji", "status": "supported", "evidence": [{"source": "S1", "quote": "kutipan"}]}]}
    assert "kutipan" in render(data)
    data["claims"][0]["evidence"][0]["source"] = "unknown"
    with pytest.raises(ValueError):
        validate(data)
    data["claims"][0]["evidence"] = []
    with pytest.raises(ValueError):
        validate(data)


def test_alur_mempertahankan_kegagalan_dan_melewati_tahap_berikut(tmp_path):
    import sys
    stages = [{"name": "bad", "command": [sys.executable, "-c", "raise SystemExit(7)"]},
              {"name": "later", "command": [sys.executable, "-c", "print(1)"]}]
    report = run(stages, tmp_path, tmp_path / "logs")
    assert report["status"] == "failed" and len(report["stages"]) == 1
    assert report["stages"][0]["returncode"] == 7


def test_alur_memeriksa_artefak_dan_waktu_habis(tmp_path):
    import sys
    result = run([{"name": "no-file", "command": [sys.executable, "-c", "pass"], "artifacts": ["missing"]}], tmp_path, tmp_path / "a")
    assert result["status"] == "failed"
    result = run([{"name": "slow", "command": [sys.executable, "-c", "import time; time.sleep(2)"], "timeout": .05}], tmp_path, tmp_path / "b")
    assert result["stages"][0]["returncode"] == 124


def test_antrean_mendeduplikasi_dan_mendeteksi_konflik_payload(tmp_path):
    q = Queue(tmp_path / "queue.db")
    q.enqueue("Tugas-A", {"numbers": [1, 2]})
    q.enqueue("Tugas-A", {"numbers": [1, 2]})
    assert len(q.jobs()) == 1
    with pytest.raises(ValueError):
        q.enqueue("Tugas-A", {"numbers": [9]})
    assert work_once(q)
    assert q.jobs()[0]["state"] == "done"
    assert json.loads(q.jobs()[0]["result"]) == {"sum": 3}


def test_pemulihan_antrean_menolak_pemilik_kedaluwarsa(tmp_path):
    q = Queue(tmp_path / "queue.db")
    q.enqueue("Tugas-A", {"numbers": [1]})
    old = q.claim(lease_seconds=10, now=100)
    assert q.claim(now=105) is None
    new = q.claim(now=111)
    assert new["owner"] != old["owner"]
    assert not q.finish(old, result="stale", now=112)
    assert q.heartbeat(new, now=112)
    assert q.finish(new, result="fresh", now=113)


def test_antrean_membatasi_percobaan_dan_mempertahankan_status_setelah_mulai_ulang(tmp_path):
    path = tmp_path / "queue.db"
    q = Queue(path)
    q.enqueue("A", {}, max_attempts=2)
    first = q.claim(now=100)
    assert q.finish(first, error="failure", now=101)
    second = q.claim(lease_seconds=1, now=102)
    assert second
    restarted = Queue(path)
    assert restarted.claim(now=104) is None
    assert restarted.jobs()[0]["state"] == "dead"


def test_pengambilan_antrean_serentak_bersifat_eksklusif(tmp_path):
    q = Queue(tmp_path / "queue.db")
    for i in range(8):
        q.enqueue(str(i), {"numbers": [i]})
    with ThreadPoolExecutor(max_workers=8) as executor:
        claimed = list(executor.map(lambda _: q.claim(), range(8)))
    assert len({j["id"] for j in claimed}) == 8
