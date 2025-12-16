"""APA 6th formatter implementation."""
from __future__ import annotations

from typing import List

from ..reference import Reference
from .shared import author_initials, join_clauses, normalize_page_range, preferred_locator, sentence_case


def format_apa(reference: Reference) -> str:
    """Format a reference using simplified APA 6th rules."""
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
    authors = _apa_authors(raw_authors)
    if len(raw_authors) == 1 and raw_authors[0] not in authors:
        # Preserve the original single author text for edge-case readability.
        authors = f"{authors} ({raw_authors[0]})" if authors else raw_authors[0]
    return authors


def _apa_authors(authors: List[str]) -> str:
    formatted = author_initials(authors)
    if not formatted:
        return ""
    if len(formatted) == 1:
        return formatted[0]
    if len(formatted) <= 7:
        return ", ".join(formatted[:-1]) + f", & {formatted[-1]}"
    # APA 6th: first six authors, ellipsis, final author
    leading = ", ".join(formatted[:6])
    trailing = formatted[-1]
    return f"{leading}, ... {trailing}"


def _year_section(reference: Reference) -> str:
    return f"({reference.year})." if reference.year else ""


def _title_section(reference: Reference) -> str:
    title = sentence_case(reference.title or "")
    if not title:
        return ""
    if reference.report_number:
        return f"{title} (Report No. {reference.report_number})."
    return f"{title}."


def _container_section(reference: Reference) -> str:
    container = reference.primary_container()
    if not container:
        return ""
    volume_issue = _volume_issue(reference.volume, reference.issue)
    pages = normalize_page_range(reference.pages) or ""
    # Journal article
    if reference.journal:
        return join_clauses([container, volume_issue, pages]) + "."
    # Chapter in book
    if reference.booktitle:
        chapter_pages = f"(pp. {pages})" if pages else ""
        edition = f"({reference.edition})" if reference.edition else ""
        return join_clauses(
            [f"In {reference.booktitle}", edition, chapter_pages, reference.publisher or ""]
        ) + "."
    # Conference paper
    if reference.event_title:
        chapter_pages = f"(pp. {pages})" if pages else ""
        location = reference.event_location or reference.place or ""
        return join_clauses([f"In {reference.event_title}", chapter_pages, location, reference.publisher or ""]) + "."
    # Book or report / web
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
    locator = preferred_locator(reference)
    if not locator:
        return ""
    if reference.doi and not reference.doi.lower().startswith("http"):
        return f"https://doi.org/{reference.doi}"
    return locator


__all__ = ["format_apa"]
