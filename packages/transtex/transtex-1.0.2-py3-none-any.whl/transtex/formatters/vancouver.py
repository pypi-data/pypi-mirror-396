"""Vancouver (NLM) formatter."""
from __future__ import annotations

from typing import List, Optional

from ..reference import Reference
from .shared import abbreviate_page_range, name_parts, normalize_page_range, preferred_locator, sentence_case


def format_vancouver(reference: Reference) -> str:
    sections: List[Optional[str]] = [
        _author_section(reference),
        _title_section(reference),
        *_source_sections(reference),
        _locator_section(reference),
    ]
    sentence = " ".join(section.strip() for section in sections if section)
    if sentence and not sentence.endswith("."):
        sentence += "."
    return sentence


def _author_section(reference: Reference) -> str:
    authors = _vancouver_authors(reference.normalized_authors())
    if not authors:
        return ""
    return f"{authors.rstrip('.').strip()}."


def _vancouver_authors(authors: List[str]) -> str:
    converted = []
    for name in authors:
        last, given_names = name_parts(name)
        if not last:
            converted.append(name.strip())
            continue
        initials = "".join(part[0].upper() for part in given_names if part)
        converted.append(f"{last} {initials}".strip())
    return ", ".join(converted)


def _title_section(reference: Reference) -> str:
    title = sentence_case(reference.title or "")
    return f"{title}." if title else ""


def _source_sections(reference: Reference) -> List[str]:
    return _journal_segments(reference) if reference.journal else _book_segments(reference)


def _journal_segments(reference: Reference) -> List[str]:
    timeline = _timeline(reference.year, reference.volume, reference.issue, reference.pages)
    return [f"{reference.journal}.", f"{timeline}."]


def _timeline(year: str | None, volume: str | None, issue: str | None, pages: str | None) -> str:
    parts = [year or "n.d."]
    volume_issue = _volume_issue(volume, issue)
    if volume_issue:
        parts.append(volume_issue)
    normalized_pages = abbreviate_page_range(pages) or normalize_page_range(pages)
    if normalized_pages:
        parts.append(f":{normalized_pages}")
    return "".join(parts)


def _volume_issue(volume: str | None, issue: str | None) -> str:
    if volume and issue:
        return f";{volume}({issue})"
    if volume:
        return f";{volume}"
    if issue:
        return f";({issue})"
    return ""


def _book_segments(reference: Reference) -> List[str]:
    segments: List[str] = []
    publisher_bits = [bit for bit in (reference.place, reference.publisher, reference.year) if bit]
    if publisher_bits:
        segments.append("; ".join(publisher_bits) + ".")
    normalized_pages = abbreviate_page_range(reference.pages) or normalize_page_range(reference.pages)
    if normalized_pages:
        segments.append(f"{normalized_pages}.")
    return segments


def _locator_section(reference: Reference) -> str:
    locator = preferred_locator(reference, prefix_doi="doi:")
    if not locator:
        return ""
    return locator if locator.endswith(".") else f"{locator}."


__all__ = ["format_vancouver"]
