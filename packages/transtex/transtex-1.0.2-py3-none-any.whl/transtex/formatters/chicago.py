"""Chicago (author-date) formatter."""
from __future__ import annotations

from typing import List, Optional

from ..reference import Reference
from .shared import (
    build_detail_section,
    format_author_list,
    join_clauses,
    join_with_period,
    normalize_page_range,
    preferred_locator,
    sentence_case,
    title_case,
)


def format_chicago(reference: Reference) -> str:
    pieces: List[Optional[str]] = [
        _author_segment(reference),
        reference.year or "n.d.",
        _title_segment(reference),
        _detail_segment(reference),
        preferred_locator(reference, prefix_doi="https://doi.org/"),
    ]
    return join_with_period(piece for piece in pieces if piece)


def _author_segment(reference: Reference) -> str:
    return _chicago_authors(reference.normalized_authors())


def _chicago_authors(authors: List[str]) -> str:
    return format_author_list(
        authors,
        invert_first=True,
        conjunction="and",
        separator=",",
        final_separator=",",
        max_names=3,
        et_al_after_first=True,
    )


def _title_segment(reference: Reference) -> str:
    if not reference.title:
        return ""
    title = title_case(reference.title)
    if reference.journal or reference.booktitle or reference.event_title:
        return f'"{title}."'
    return title


def _detail_segment(reference: Reference) -> str:
    if reference.journal:
        return _journal_detail(reference)
    return _non_journal_detail(reference)


def _journal_detail(reference: Reference) -> str:
    volume_issue = _volume_issue(reference.volume, reference.issue)
    journal = join_clauses([reference.journal, volume_issue], separator=" ")
    pages = normalize_page_range(reference.pages)
    page_segment = f": {pages}" if pages else ""
    return f"{journal}{page_segment}".strip()


def _volume_issue(volume: str | None, issue: str | None) -> str:
    if volume and issue:
        return f"{volume} ({issue})"
    if volume:
        return volume
    return ""


def _non_journal_detail(reference: Reference) -> str:
    if reference.event_title:
        pages = normalize_page_range(reference.pages)
        location = reference.event_location or reference.place
        return join_clauses(
            [
                f"In {reference.event_title}",
                f"{pages}" if pages else "",
                location or "",
                reference.publisher or reference.institution or "",
                reference.year or "",
            ]
        )
    book_phrase = _book_phrase(reference.booktitle, reference.pages)
    publisher = reference.publisher or reference.institution or ""
    place = reference.place or ""
    year = reference.year or ""
    if book_phrase:
        return join_clauses([book_phrase, place, publisher, year])
    return join_clauses([place, publisher, year])


def _book_phrase(booktitle: str | None, pages: str | None) -> Optional[str]:
    if not booktitle:
        return None
    page_clause = f", {pages}" if pages else ""
    return f"In *{booktitle}*{page_clause}"


__all__ = ["format_chicago"]
