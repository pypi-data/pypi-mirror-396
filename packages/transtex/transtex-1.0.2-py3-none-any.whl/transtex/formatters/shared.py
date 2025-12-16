"""Shared utilities for formatter implementations."""
from __future__ import annotations

import re
from typing import Iterable, List, Optional, Sequence, Tuple

from ..reference import Reference


def preferred_locator(reference: Reference, prefix_doi: str = "") -> str:
    """Return DOI or URL with an optional prefix for DOI values."""
    if reference.doi:
        doi = reference.doi.strip()
        lowered = doi.lower()
        if lowered.startswith("http"):
            # Treat DOI URLs as canonical DOI strings to keep output consistent.
            doi_value = doi
            if "doi.org/" in lowered:
                doi_value = doi.split("doi.org/", 1)[1]
            if prefix_doi:
                glue = "" if prefix_doi.endswith((" ", ":", "/")) else " "
                return f"{prefix_doi}{glue}{doi_value}"
            return doi_value
        if lowered.startswith("10."):
            if prefix_doi:
                glue = "" if prefix_doi.endswith((" ", ":", "/")) else " "
                return f"{prefix_doi}{glue}{doi}"
            return doi
        return doi
    if reference.url:
        return reference.url
    return ""


def split_name_with_initials(name: str) -> Tuple[str, List[str]]:
    """Return last name and a list of initials for APA/IEEE style."""
    raw = name.strip()
    if not raw:
        return "", []
    if "," in raw:
        last, remaining = raw.split(",", 1)
        given_names = [chunk.strip() for chunk in remaining.split() if chunk.strip()]
        initials = [f"{part[0].upper()}" for part in given_names]
        initials = [f"{initial}." for initial in initials if initial]
        return last.strip(), initials
    parts = raw.split()
    if not parts:
        return "", []
    last = parts[-1]
    initials = [f"{part[0].upper()}." for part in parts[:-1]]
    return last, initials


def name_parts(name: str) -> Tuple[str, List[str]]:
    """Return last name and given-name parts without punctuation."""
    raw = name.strip()
    if not raw:
        return "", []
    if "," in raw:
        last, remaining = raw.split(",", 1)
        given_names = [chunk.strip() for chunk in remaining.split() if chunk.strip()]
        return last.strip(), given_names
    parts = raw.split()
    if not parts:
        return "", []
    return parts[-1], parts[:-1]


def format_name(name: str, invert: bool = False) -> str:
    """Format a full name optionally in inverted form."""
    last, given = name_parts(name)
    if not last:
        return name.strip()
    given_text = " ".join(given).strip()
    if invert:
        return f"{last}, {given_text}".strip().strip(",")
    return f"{given_text} {last}".strip()


def format_author_list(
    authors: Sequence[str],
    *,
    invert_first: bool = True,
    conjunction: str = "and",
    separator: str = ",",
    final_separator: str = ",",
    max_names: int | None = None,
    et_al_text: str = "et al.",
    et_al_after_first: bool = False,
    et_al_separator: str = ", ",
) -> str:
    """Format a list of authors with configurable inversion and joining rules."""
    formatted = [
        format_name(name, invert=invert_first and index == 0) or name.strip()
        for index, name in enumerate(authors)
    ]
    formatted = [name for name in formatted if name]
    if not formatted:
        return ""
    if max_names is not None and len(formatted) > max_names:
        if et_al_after_first:
            return f"{formatted[0]}{et_al_separator}{et_al_text}".strip()
        formatted = formatted[:max_names] + [et_al_text]
    if len(formatted) == 1:
        return formatted[0]
    if len(formatted) == 2:
        joiner = f"{final_separator} {conjunction} " if final_separator else f" {conjunction} "
        return f"{formatted[0]}{joiner}{formatted[1]}".strip()
    body = f"{separator} ".join(formatted[:-1])
    tail = f"{final_separator} {conjunction} " if final_separator else f" {conjunction} "
    return f"{body}{tail}{formatted[-1]}".strip()


def build_detail_section(
    container: Optional[str],
    volume_issue: Optional[str],
    publisher: Optional[str],
    year: Optional[str],
    pages: Optional[str],
    locator: Optional[str],
) -> str:
    """Create a comma-delimited detail section with locator appended if present."""
    segments = []
    if publisher:
        segments.append(publisher)
    if container:
        segments.append(container)
    if volume_issue:
        segments.append(volume_issue)
    if year:
        segments.append(year)
    if pages:
        segments.append(pages)
    detail = ", ".join(segment for segment in segments if segment)
    if locator:
        detail = f"{detail}, {locator}" if detail else locator
    if detail and not detail.endswith("."):
        detail += "."
    return detail


def join_with_period(parts: Iterable[str]) -> str:
    """Join the provided strings with sentence-style periods."""
    cleaned = [segment.strip() for segment in parts if segment.strip()]
    if not cleaned:
        return ""
    sentence = cleaned[0]
    for segment in cleaned[1:]:
        separator = " " if _ends_with_terminal(sentence) else ". "
        sentence = f"{sentence}{separator}{segment}"
    if sentence and sentence[-1] not in ".!?\"":
        sentence += "."
    return sentence


def _ends_with_terminal(text: str) -> bool:
    if not text:
        return False
    terminal_patterns = (".", "!", "?", '."',"!\"","?\"",".'","!'","?'")
    return any(text.endswith(pattern) for pattern in terminal_patterns)


def join_clauses(parts: Iterable[str], *, separator: str = ", ") -> str:
    """Join clauses with a separator while ignoring empty fragments."""
    cleaned = [segment.strip() for segment in parts if segment and segment.strip()]
    return separator.join(cleaned)


def author_initials(authors: Sequence[str], *, split_initials: bool = True) -> List[str]:
    """Return a list of authors formatted as 'Last, I. I.'."""
    converted: List[str] = []
    for author in authors:
        last, initials = split_name_with_initials(author)
        if not last:
            converted.append(author.strip())
            continue
        joined_initials = " ".join(initials) if split_initials else "".join(initials)
        name = f"{last}, {joined_initials}" if joined_initials else last
        converted.append(name.strip().strip(","))
    return converted


def sentence_case(text: str) -> str:
    """Convert a title to sentence case while preserving all-caps tokens."""
    if not text:
        return ""
    parts = re.split(r"(\s+)", text.strip())
    result: List[str] = []
    first_word_done = False
    for part in parts:
        if not part.strip():
            result.append(part)
            continue
        if not first_word_done:
            result.append(part[:1].upper() + part[1:].lower())
            first_word_done = True
            continue
        if part.isupper():
            result.append(part)
        else:
            result.append(part.lower())
    return "".join(result)


def normalize_page_range(pages: str | None) -> str | None:
    """Normalize page ranges to use an en dash between numbers."""
    if not pages:
        return None
    return re.sub(r"(?<=\d)-(?=\d)", "–", pages)


def abbreviate_page_range(pages: str | None) -> str | None:
    """Abbreviate page ranges per Vancouver guidance (e.g., 452–468 -> 452–68)."""
    if not pages:
        return None
    normalized = normalize_page_range(pages)
    if not normalized or "–" not in normalized:
        return normalized
    start, end = normalized.split("–", 1)
    if not start.isdigit() or not end.isdigit():
        return normalized
    if len(start) != len(end):
        return normalized
    # Drop shared leading digits from end.
    shared_prefix = 0
    for a, b in zip(start, end):
        if a == b:
            shared_prefix += 1
        else:
            break
    abbreviated_end = end[shared_prefix:] if shared_prefix < len(end) else end
    abbreviated_end = abbreviated_end or end
    return f"{start}–{abbreviated_end}"


def title_case(text: str) -> str:
    """Convert text to basic title case while keeping small words lower."""
    if not text:
        return ""
    small_words = {
        "a",
        "an",
        "the",
        "and",
        "but",
        "or",
        "nor",
        "for",
        "so",
        "yet",
        "on",
        "in",
        "to",
        "of",
        "by",
        "at",
        "from",
    }
    tokens = re.split(r"(\s+)", text.strip())
    result: List[str] = []
    first_word = True
    for token in tokens:
        if not token.strip():
            result.append(token)
            continue
        word = token
        lowered = word.lower()
        if first_word or lowered not in small_words:
            word = word[0].upper() + word[1:]
        else:
            word = lowered
        first_word = False
        result.append(word)
    return "".join(result)


__all__ = [
    "preferred_locator",
    "split_name_with_initials",
    "name_parts",
    "format_name",
    "format_author_list",
    "build_detail_section",
    "join_with_period",
    "join_clauses",
    "author_initials",
    "sentence_case",
    "normalize_page_range",
    "title_case",
    "abbreviate_page_range",
]
