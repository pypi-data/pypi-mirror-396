"""IEEE formatter implementation."""
from __future__ import annotations

from typing import List

from ..reference import Reference
from .shared import normalize_page_range, preferred_locator, split_name_with_initials, title_case

_IEEE_MAX_AUTHORS = 6


def format_ieee(reference: Reference) -> str:
    """Format a reference using simplified IEEE rules."""
    container = reference.primary_container()
    if container and reference.journal:
        segments = [
            _author_segment(reference),
            _title_segment(reference),
            container,
            _volume_issue_segment(reference),
            _pages_segment(reference),
            reference.year or "",
            preferred_locator(reference, prefix_doi="doi: "),
        ]
    else:
        # Book/chapters/web: Author, Title, container/booktitle/publisher, year, locator.
        segments = [
            _author_segment(reference),
            _title_segment(reference),
            reference.booktitle or container or reference.publisher or "",
            reference.place or "",
            reference.publisher if reference.booktitle else "",
            _pages_segment(reference),
            reference.year or "",
            preferred_locator(reference, prefix_doi="doi: "),
        ]
    sentence = _join_ieee_segments(segments)
    return f"{sentence}." if sentence else ""


def _author_segment(reference: Reference) -> str:
    authors = [_ieee_name(author) for author in reference.normalized_authors()]
    if not authors:
        return ""
    if len(authors) > _IEEE_MAX_AUTHORS:
        return f"{authors[0]} et al."
    return _join_authors(authors)


def _join_authors(authors: List[str]) -> str:
    if not authors:
        return ""
    if len(authors) == 1:
        return authors[0]
    if len(authors) == 2:
        return " and ".join(authors)
    return ", ".join(authors[:-1]) + ", and " + authors[-1]


def _title_segment(reference: Reference) -> str:
    if not reference.title:
        return ""
    return f'"{title_case(reference.title)},"'


def _volume_issue_segment(reference: Reference) -> str:
    if reference.volume:
        pieces: List[str] = [f"vol. {reference.volume}"]
        if reference.issue:
            pieces.append(f"no. {reference.issue}")
        return ", ".join(pieces)
    if reference.issue:
        return f"no. {reference.issue}"
    return ""


def _pages_segment(reference: Reference) -> str:
    pages = normalize_page_range(reference.pages)
    return f"pp. {pages}" if pages else ""


def _join_ieee_segments(parts: List[str | None]) -> str:
    cleaned = [part.strip() for part in parts if part and part.strip()]
    if not cleaned:
        return ""
    assembled = [cleaned[0]]
    for previous, current in zip(cleaned, cleaned[1:]):
        separator = " " if previous.endswith(',"') else ", "
        assembled.append(f"{separator}{current}")
    return "".join(assembled)


def _ieee_name(author: str) -> str:
    last, initials = split_name_with_initials(author)
    if not last:
        return author.strip()
    joined_initials = " ".join(initials)
    if joined_initials:
        return f"{joined_initials} {last}"
    return last


__all__ = ["format_ieee"]
