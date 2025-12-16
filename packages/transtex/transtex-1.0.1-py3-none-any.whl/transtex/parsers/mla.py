"""Parse MLA 9th citations."""
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


def parse_mla_citation(text: str) -> Reference:
    raw = text.strip()
    if not raw:
        raise ValueError("Empty MLA citation string")

    title_match = re.search(r"\"(.+?)\"", raw)
    if not title_match:
        raise ValueError("MLA citation missing title")
    authors_segment = raw[: title_match.start()].strip().rstrip(".")
    title = strip_trailing_period(title_match.group(1).strip())
    after_title = raw[title_match.end() :].strip()

    locator = None
    locator_match = re.search(r"(https?://\S+|10\.\S+)\.?$", after_title)
    if locator_match:
        locator = locator_match.group(1).strip()
        after_title = after_title[: locator_match.start()].strip().rstrip(",")

    container = None
    year = None
    publisher = None
    if "vol." in after_title.lower() or "no." in after_title.lower():
        container = after_title.split(",", 1)[0].strip()
    else:
        # Attempt book/web form: Publisher, Year
        parts = [piece.strip() for piece in after_title.split(",") if piece.strip()]
        if parts:
            publisher = parts[0]
        if len(parts) > 1 and re.fullmatch(r"\d{4}", parts[1]):
            year = parts[1]

    volume = None
    issue = None
    pages = None
    vol_match = re.search(r"vol\.\s*([\w]+)", after_title, re.IGNORECASE)
    if vol_match:
        volume = vol_match.group(1)
    issue_match = re.search(r"no\.\s*([\w]+)", after_title, re.IGNORECASE)
    if issue_match:
        issue = issue_match.group(1)
    year_match = re.search(r"(\d{4})", after_title)
    if year_match:
        year = year_match.group(1)
    pages_match = re.search(r"pp\.\s*([\w–-]+)", after_title, re.IGNORECASE)
    if pages_match:
        pages = normalize_pages(pages_match.group(1))

    reference = Reference(
        entry_type="article" if container else "book",
        cite_key=generate_cite_key([], year, title),
        title=title,
        authors=_parse_authors(authors_segment),
        journal=container,
        volume=volume,
        issue=issue,
        pages=pages,
        year=year,
        publisher=publisher,
    )
    doi, url = clean_locator(locator)
    reference.doi = doi
    reference.url = url
    return reference


def _parse_authors(segment: str) -> list[str]:
    cleaned = segment.rstrip(".").strip()
    if "et al." in cleaned:
        head = cleaned.split(" et al.", 1)[0].strip().rstrip(",")
        return [head, "et al."] if head else ["et al."]
    if " and " in cleaned:
        first, second = cleaned.split(" and ", 1)
        return [first.strip().rstrip(","), second.strip()]
    return [cleaned] if cleaned else []


__all__ = ["parse_mla_citation"]
