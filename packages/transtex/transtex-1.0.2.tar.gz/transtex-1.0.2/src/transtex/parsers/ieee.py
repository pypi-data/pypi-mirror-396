"""Parse IEEE-style citations."""
from __future__ import annotations

import re

from ..reference import Reference
from .shared import clean_locator, generate_cite_key, normalize_pages, split_authors_delimited


def parse_ieee_citation(text: str) -> Reference:
    raw = text.strip().rstrip(".")
    if not raw:
        raise ValueError("Empty IEEE citation string")

    title_match = re.search(r"\"([^\"]+)\"", raw)
    if not title_match:
        raise ValueError("IEEE citation missing title content")
    title = title_match.group(1).strip().rstrip(",")
    authors_segment = raw[: title_match.start()].rstrip(", ").strip()
    post_title = raw[title_match.end() :].strip()

    tokens = [token.strip() for token in post_title.split(",") if token.strip()]
    if not tokens:
        raise ValueError("IEEE citation missing container segment")

    container = tokens[0]
    volume = issue = pages = year = doi = url = None
    for token in tokens[1:]:
        lowered = token.lower()
        if lowered.startswith("vol."):
            volume = token.split(" ", 1)[1].strip()
        elif lowered.startswith("no."):
            issue = token.split(" ", 1)[1].strip()
        elif lowered.startswith("pp."):
            pages = normalize_pages(token.split(" ", 1)[1].strip())
        elif lowered.startswith("doi"):
            doi = token.split(":", 1)[-1].strip()
        elif token.startswith("10."):
            doi = token.strip()
        elif lowered.startswith("http"):
            doi_candidate, url_candidate = clean_locator(token)
            if doi_candidate:
                doi = doi_candidate
            elif url_candidate:
                url = url_candidate
        elif re.fullmatch(r"\d{4}", token):
            year = token

    authors = _parse_authors(authors_segment)
    cite_key = generate_cite_key(authors, year, title)
    reference = Reference(
        entry_type="article",
        cite_key=cite_key,
        title=title or None,
        authors=authors,
        journal=container or None,
        volume=volume,
        issue=issue,
        pages=pages,
        year=year,
        doi=doi,
        url=url,
    )
    return reference


def _parse_authors(segment: str) -> list[str]:
    parts = split_authors_delimited(segment, separators=[", and ", " and ", ", "])
    return [part.strip() for part in parts if part.strip()]


__all__ = ["parse_ieee_citation"]
