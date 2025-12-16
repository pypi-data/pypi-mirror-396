"""Parse APA-style citations (6th/7th simplified)."""
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


def parse_apa_citation(text: str) -> Reference:
    raw = text.strip()
    if not raw:
        raise ValueError("Empty APA citation string")

    year_match = re.search(r"\(([^)]+)\)\.", raw)
    if not year_match:
        raise ValueError("APA citation missing year segment '(year).'")

    authors_segment = raw[: year_match.start()].strip()
    remainder = raw[year_match.end() :].strip()
    year = year_match.group(1).strip() or None

    if ". " in remainder:
        title, remainder = remainder.split(". ", 1)
    else:
        title, remainder = remainder, ""
    title = strip_trailing_period(title.strip())

    locator = None
    locator_match = re.search(r"(https?://\S+|10\.\S+)$", remainder)
    if locator_match:
        locator = locator_match.group(1).strip()
        remainder = remainder[: locator_match.start()].strip()

    container_segment = remainder.rstrip(".").strip().replace("*", "")
    if container_segment.lower().startswith("retrieved from"):
        locator = container_segment.split(" ", 2)[-1].strip()
        container_segment = ""
    container, volume, issue, pages = _parse_container(container_segment)

    authors = _parse_authors(authors_segment)
    cite_key = generate_cite_key(authors, year, title)
    publisher_value: str | None = None
    if container and not volume and not issue and not pages:
        publisher_value = container
        container = None

    reference = Reference(
        entry_type="article",
        cite_key=cite_key,
        title=title or None,
        authors=authors,
        journal=container,
        publisher=publisher_value,
        volume=volume,
        issue=issue,
        pages=normalize_pages(pages),
        year=year,
    )
    doi, url = clean_locator(locator)
    reference.doi = doi
    reference.url = url
    return reference


def _parse_container(segment: str) -> tuple[str | None, str | None, str | None, str | None]:
    if not segment:
        return None, None, None, None
    match = re.match(
        r"(?P<container>.+?)(?:,\s*(?P<volume>\d+)(?:\((?P<issue>[^)]+)\))?)?(?:,\s*(?P<pages>[\w\-–]+))?$",
        segment,
    )
    if not match:
        return segment, None, None, None
    container = (match.group("container") or "").strip() or None
    volume = (match.group("volume") or "").strip() or None
    issue = (match.group("issue") or "").strip() or None
    pages = (match.group("pages") or "").strip() or None
    # Handle "Retrieved from URL" tail
    if container and container.lower().startswith("retrieved from"):
        return None, None, None, None
    return container, volume, issue, pages


def _parse_authors(segment: str) -> list[str]:
    parts = split_authors_delimited(segment, separators=[", &", " &", " and "])
    authors = []
    for part in parts:
        name = part.strip().lstrip("& ").strip()
        if not name:
            continue
        if not name.endswith("."):
            name += "."
        authors.append(name)
    return authors


__all__ = ["parse_apa_citation"]
