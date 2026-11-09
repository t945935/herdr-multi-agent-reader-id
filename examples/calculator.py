"""Chapter 1: kontrak kecil untuk latihan pengembangan dan tinjauan."""

from math import isfinite


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Diharapkan angka, selain bool")
    if not isfinite(value):
        raise ValueError("Diharapkan angka berhingga")
    return value


def add(a, b):
    return _number(a) + _number(b)


def subtract(a, b):
    return _number(a) - _number(b)


def multiply(a, b):
    return _number(a) * _number(b)


def divide(a, b):
    a, b = _number(a), _number(b)
    if b == 0:
        raise ZeroDivisionError("Tidak dapat membagi dengan nol")
    return a / b
