"""Kontrak bersama bab 2/4/5/6; peringkat kompetisi memakai total tanpa pembulatan."""

from collections.abc import Mapping
from math import isfinite

SUBJECTS = frozenset({"English", "History", "Mathematics"})


def validate_scores(scores):
    if not isinstance(scores, Mapping) or set(scores) != SUBJECTS:
        raise ValueError("scores harus berisi tepat English, History, dan Mathematics")
    for value in scores.values():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("Nilai harus berupa angka, bukan bool")
        if not isfinite(value) or not 0 <= value <= 100:
            raise ValueError("Nilai harus berhingga dan antara 0 dan 100")
    return scores


def calculate_total(scores):
    return sum(validate_scores(scores).values())


def calculate_average(scores):
    return calculate_total(scores) / 3


def get_grade(average):
    if isinstance(average, bool) or not isinstance(average, (int, float)):
        raise ValueError("Rata-rata harus berupa angka")
    if not isfinite(average) or not 0 <= average <= 100:
        raise ValueError("Rata-rata harus antara 0 dan 100")
    return "Lulus" if average >= 60 else "Tidak lulus"


def rank_students(students):
    if not isinstance(students, list):
        raise ValueError("students harus berupa daftar")
    rows = []
    for student in students:
        if not isinstance(student, Mapping):
            raise ValueError("Setiap siswa harus berupa objek")
        name = student.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Nama siswa wajib diisi")
        total = calculate_total(student.get("scores"))
        average = total / 3
        rows.append({"name": name.strip(), "scores": dict(student["scores"]),
                     "total": total, "average": average, "grade": get_grade(average)})
    rows.sort(key=lambda row: row["total"], reverse=True)
    previous = None
    rank = 0
    for index, row in enumerate(rows, 1):
        if previous is None or row["total"] != previous:
            rank = index
        previous = row["total"]
        row["rank"] = rank
    return rows
