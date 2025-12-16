"""Parse Chicago author-date citations."""
from __future__ import annotations

import re

from ..reference import Reference
from .shared import (
    clean_locator,
    generate_cite_key,
    normalize_pages,
    split_authors_delimited,
    strip_trailing_period,
)


def parse_chicago_citation(text: str) -> Reference:
    raw = text.strip()
    if not raw:
        raise ValueError("Empty Chicago citation string")

    match = re.match(r"^(?P<authors>.*?)\.\s+(?P<year>\d{4}|n\.d\.)\.\s+(?P<rest>.+)$", raw)
    if not match:
        raise ValueError("Chicago citation missing expected segments")
    authors_segment = match.group("authors").strip()
    year = strip_trailing_period(match.group("year").strip()) or None
    remainder = match.group("rest").strip()

    title_match = re.search(r"\"(.+?)\"", remainder)
    if not title_match:
        raise ValueError("Chicago citation missing title")
    title = strip_trailing_period(title_match.group(1).strip())
    after_title = remainder[title_match.end() :].strip()

    locator = None
    locator_match = re.search(r"(https?://\S+|10\.\S+)$", after_title)
    if locator_match:
        locator = locator_match.group(1).strip()
        after_title = after_title[: locator_match.start()].strip()
    after_title = after_title.rstrip(".").strip()

    journal_match = re.match(r"(.+?)\s+(\d+)\s*\(([^)]+)\):\s*([\w–-]+)", after_title)
    journal = volume = issue = pages = None
    if journal_match:
        journal = journal_match.group(1).strip()
        volume = journal_match.group(2).strip()
        issue = journal_match.group(3).strip()
        pages = normalize_pages(journal_match.group(4).strip())
    else:
        place_publisher = re.match(r"([^:]+):\s*([^,]+)", after_title)
        publisher = None
        place = None
        if place_publisher:
            place = place_publisher.group(1).strip()
            publisher = place_publisher.group(2).strip()
        reference = Reference(
            entry_type="book",
            cite_key=generate_cite_key([], year, title),
            title=title,
            authors=_parse_authors(authors_segment),
            publisher=publisher,
            place=place,
            year=year,
        )
        doi, url = clean_locator(locator)
        reference.doi = doi
        reference.url = url
        return reference

    reference = Reference(
        entry_type="article",
        cite_key=generate_cite_key([], year, title),
        title=title,
        authors=_parse_authors(authors_segment),
        journal=journal,
        volume=volume,
        issue=issue,
        pages=pages,
        year=year,
    )
    doi, url = clean_locator(locator)
    reference.doi = doi
    reference.url = url
    return reference


def _parse_authors(segment: str) -> list[str]:
    cleaned = segment.rstrip(".").strip()
    if " and " in cleaned:
        first, second = cleaned.split(" and ", 1)
        authors = [first.strip().rstrip(",")]
        authors.append(second.strip())
        return [author for author in authors if author]
    return [cleaned] if cleaned else []


__all__ = ["parse_chicago_citation"]
