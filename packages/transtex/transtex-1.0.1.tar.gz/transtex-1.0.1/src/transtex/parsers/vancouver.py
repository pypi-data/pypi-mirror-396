"""Parse Vancouver (NLM) citations."""
from __future__ import annotations

import re

from ..reference import Reference
from .shared import capitalize_sentence, clean_locator, generate_cite_key, normalize_pages


def parse_vancouver_citation(text: str) -> Reference:
    raw = text.strip()
    if not raw:
        raise ValueError("Empty Vancouver citation string")

    match = re.match(
        r"^(?P<authors>[^.]+)\.\s+(?P<title>[^.]+)\.\s+(?P<journal>[^.]+)\.\s+(?P<timeline>[^.]+)\.?\s*(?P<locator>.*)$",
        raw,
    )
    if not match:
        raise ValueError("Vancouver citation missing expected segments")

    authors_segment = match.group("authors").strip()
    title = capitalize_sentence(match.group("title").strip())
    journal_segment = match.group("journal").strip()
    timeline_segment = match.group("timeline").strip()
    locator_segment = match.group("locator").strip()

    year = volume = issue = pages = None
    timeline_match = re.match(r"(\d{4});?([\d()]+)?:?([\w–-]+)?", timeline_segment)
    if timeline_match:
        year = timeline_match.group(1)
        vol_issue = timeline_match.group(2) or ""
        if "(" in vol_issue and ")" in vol_issue:
            volume = vol_issue.split("(", 1)[0]
            issue = vol_issue.split("(", 1)[1].rstrip(")")
        else:
            volume = vol_issue if vol_issue else None
        pages = normalize_pages(timeline_match.group(3) or None)

    reference = Reference(
        entry_type="article",
        cite_key=generate_cite_key([], year, title),
        title=title,
        authors=_parse_authors(authors_segment),
        journal=journal_segment,
        volume=volume,
        issue=issue,
        pages=pages,
        year=year,
    )

    doi, url = clean_locator(locator_segment)
    reference.doi = doi
    reference.url = url
    return reference


def _parse_authors(segment: str) -> list[str]:
    cleaned = segment.strip()
    if not cleaned:
        return []
    authors: list[str] = []
    for raw in cleaned.split(","):
        name = raw.strip()
        if not name:
            continue
        parts = name.split()
        if len(parts) == 1:
            authors.append(parts[0])
            continue
        last = parts[0]
        given_parts = []
        for part in parts[1:]:
            if len(part) == 1 and not part.endswith("."):
                given_parts.append(f"{part}.")
            else:
                given_parts.append(part)
        given = " ".join(given_parts)
        authors.append(f"{given} {last}".strip())
    return authors


__all__ = ["parse_vancouver_citation"]
