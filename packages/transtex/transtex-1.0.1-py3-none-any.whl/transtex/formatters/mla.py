"""MLA 9th Works Cited formatter."""
from __future__ import annotations

from typing import List, Optional

from ..reference import Reference
from .shared import build_detail_section, format_author_list, normalize_page_range, preferred_locator, title_case


def format_mla(reference: Reference) -> str:
    sections: List[Optional[str]] = [
        _author_section(reference),
        _title_section(reference),
        _detail_section(reference),
    ]
    sentence = " ".join(section.strip() for section in sections if section)
    if sentence and not sentence.endswith("."):
        sentence += "."
    return sentence


def _mla_authors(authors: List[str]) -> str:
    return format_author_list(
        authors,
        invert_first=True,
        conjunction="and",
        separator=",",
        final_separator=",",
        max_names=2,
        et_al_after_first=True,
    )


def _author_section(reference: Reference) -> str:
    author_text = _mla_authors(reference.normalized_authors())
    return f"{author_text}." if author_text else ""


def _title_section(reference: Reference) -> str:
    if not reference.title:
        return ""
    if reference.primary_container():
        return f'"{title_case(reference.title)}."'
    return f"{title_case(reference.title)}."


def _detail_section(reference: Reference) -> str:
    container = reference.primary_container()
    publisher = reference.publisher or ""
    # Keep publisher for book/collected works even when container exists.
    include_publisher = bool(publisher and (not reference.journal))
    volume_issue = _volume_issue(reference)
    pages_value = normalize_page_range(reference.pages)
    pages = f"pp. {pages_value}" if pages_value else ""

    # Books without container
    if not container and publisher:
        detail_parts = [publisher]
        if reference.place:
            detail_parts.insert(0, reference.place)
        detail_parts.append(reference.year or "")
        if pages:
            detail_parts.append(pages)
        detail = ", ".join(part for part in detail_parts if part)
        locator = preferred_locator(reference, prefix_doi="https://doi.org/")
        if locator:
            detail = f"{detail}. {locator}".strip()
        if detail and not detail.endswith("."):
            detail += "."
        return detail

    ordered: List[str] = [
        container or "",
        volume_issue,
        publisher if include_publisher else "",
        reference.year or "",
        pages,
    ]
    detail = ", ".join(part for part in ordered if part)
    locator = preferred_locator(reference, prefix_doi="https://doi.org/")
    if locator:
        if detail and not detail.endswith("."):
            detail += "."
        detail = f"{detail} {locator}".strip()
    if detail and not detail.endswith("."):
        detail += "."
    return detail


def _volume_issue(reference: Reference) -> str:
    bits: List[str] = []
    if reference.volume:
        bits.append(f"vol. {reference.volume}")
    if reference.issue:
        bits.append(f"no. {reference.issue}")
    return ", ".join(bits)


__all__ = ["format_mla"]
