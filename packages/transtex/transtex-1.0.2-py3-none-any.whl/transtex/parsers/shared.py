"""Shared helpers for citation parsers."""
from __future__ import annotations

import re
from typing import Iterable, List

from ..reference import Reference


def clean_locator(locator: str | None) -> tuple[str | None, str | None]:
    """Split locator into doi/url."""
    if not locator:
        return None, None
    lowered = locator.lower()
    text = locator.strip().strip(".")
    lowered = text.lower()
    if lowered.startswith("doi:"):
        candidate = text.split(":", 1)[1].strip()
        return candidate, None
    if lowered.startswith("10."):
        return text, None
    if "doi.org/" in lowered:
        _, doi_value = text.split("doi.org/", 1)
        return doi_value.strip(), None
    if lowered.startswith("http"):
        return None, text
    return None, None


def generate_cite_key(authors: list[str], year: str | None, title: str | None) -> str:
    """Generate a simple cite key from author/year/title."""
    def _slug(value: str) -> str:
        alnum = re.sub(r"[^A-Za-z0-9]+", "", value)
        return alnum.lower()

    first_author = authors[0] if authors else ""
    author_piece = _slug(first_author.split(",")[0] if "," in first_author else first_author.split()[-1] if first_author else "anon")
    year_piece = _slug(year or "nd")
    title_piece = _slug(title or "")
    key_parts = [part for part in (author_piece, year_piece, title_piece) if part]
    return "".join(key_parts) or "reference"


def normalize_pages(pages: str | None) -> str | None:
    """Normalize hyphen to en dash for page ranges."""
    if not pages:
        return None
    cleaned = pages.strip().rstrip(".,;")
    return re.sub(r"(?<=\d)-(?=\d)", "–", cleaned)


def strip_trailing_period(text: str) -> str:
    return text[:-1] if text.endswith(".") else text


def split_authors_delimited(segment: str, separators: Iterable[str]) -> list[str]:
    """Split authors by provided delimiters."""
    cleaned = segment.strip().rstrip(".")
    if not cleaned:
        return []
    pattern = "|".join(re.escape(sep) for sep in separators)
    parts = re.split(pattern, cleaned)
    return [part.strip() for part in parts if part.strip()]


def capitalize_sentence(text: str) -> str:
    """Capitalize first letter of the sentence-case string."""
    if not text:
        return ""
    return text[0].upper() + text[1:]


__all__ = [
    "clean_locator",
    "generate_cite_key",
    "normalize_pages",
    "strip_trailing_period",
    "split_authors_delimited",
    "capitalize_sentence",
]
