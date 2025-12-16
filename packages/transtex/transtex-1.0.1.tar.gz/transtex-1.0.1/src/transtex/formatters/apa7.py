"""APA 7th formatter implementation."""
from __future__ import annotations

from typing import List

from ..reference import Reference
from .shared import author_initials, join_clauses, normalize_page_range, preferred_locator, sentence_case


def format_apa7(reference: Reference) -> str:
    """Format a reference using simplified APA 7th rules."""
    parts = [
        _author_section(reference),
        _year_section(reference),
        _title_section(reference),
        _container_section(reference),
        _locator_section(reference),
    ]
    return " ".join(part for part in parts if part).strip()


def _author_section(reference: Reference) -> str:
    raw_authors = reference.normalized_authors()
    authors = _apa7_authors(raw_authors)
    if len(raw_authors) == 1 and raw_authors[0] not in authors:
        authors = f"{authors} ({raw_authors[0]})" if authors else raw_authors[0]
    return authors


def _apa7_authors(authors: List[str]) -> str:
    formatted = author_initials(authors)
    count = len(formatted)
    if count == 0:
        return ""
    if count == 1:
        return formatted[0]
    if count <= 20:
        return ", ".join(formatted[:-1]) + f", & {formatted[-1]}"
    leading = ", ".join(formatted[:19])
    trailing = formatted[-1]
    return f"{leading}, ... {trailing}"


def _year_section(reference: Reference) -> str:
    return f"({reference.year})." if reference.year else ""


def _title_section(reference: Reference) -> str:
    title = sentence_case(reference.title or "")
    return f"{title}." if title else ""


def _container_section(reference: Reference) -> str:
    container = reference.primary_container()
    if not container:
        return ""
    volume_issue = _volume_issue(reference.volume, reference.issue)
    pages = normalize_page_range(reference.pages) or ""
    if reference.journal:
        return join_clauses([container, volume_issue, pages]) + "."
    if reference.booktitle:
        chapter_pages = f"(pp. {pages})" if pages else ""
        edition = f"({reference.edition})" if reference.edition else ""
        return join_clauses(
            [f"In {reference.booktitle}", edition, chapter_pages, reference.publisher or ""]
        ) + "."
    parts = [container]
    if reference.edition:
        parts.append(reference.edition)
    if reference.place:
        parts.append(reference.place)
    if reference.publisher and reference.publisher not in parts:
        parts.append(reference.publisher)
    if pages:
        parts.append(pages)
    if reference.accessed_date:
        parts.append(f"Retrieved {reference.accessed_date}")
    return join_clauses(parts) + "."


def _volume_issue(volume: str | None, issue: str | None) -> str:
    if volume and issue:
        return f"{volume}({issue})"
    if volume:
        return volume
    return ""


def _locator_section(reference: Reference) -> str:
    locator = preferred_locator(reference, prefix_doi="https://doi.org/")
    return locator or ""


__all__ = ["format_apa7"]
