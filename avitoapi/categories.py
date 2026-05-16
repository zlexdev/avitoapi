"""Static Avito category-id catalogue.

Top-level domain trees exposed as ``IntEnum``s for quick reference.
Snapshot: 2026-05-16. Source: https://developers.avito.ru/api-catalog/item/category

Avito occasionally rotates ids; consumers can override per-instance when
they hit a new tree.
"""
from __future__ import annotations

from enum import IntEnum


class Vehicles(IntEnum):
    """Subset of the Vehicles tree. Values are integer category ids."""

    CARS = 9
    MOTORCYCLES = 14
    TRUCKS = 81


class Realty(IntEnum):
    """Subset of the Realty tree."""

    FLATS = 24
    HOUSES = 25
    COMMERCIAL = 42


class Job(IntEnum):
    """Subset of the Job tree."""

    VACANCIES = 110
    RESUMES = 111


class Services(IntEnum):
    """Subset of the Services tree."""

    SERVICES = 114


class Electronics(IntEnum):
    """Subset of the Electronics tree."""

    PHONES = 84
    LAPTOPS = 96


class Hobbies(IntEnum):
    """Subset of the Hobbies tree."""

    BOOKS = 33


__all__ = [
    "Electronics",
    "Hobbies",
    "Job",
    "Realty",
    "Services",
    "Vehicles",
]
