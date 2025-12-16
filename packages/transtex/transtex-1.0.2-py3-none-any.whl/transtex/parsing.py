"""Public citation parsing interface."""
from __future__ import annotations

from typing import Callable

from .bibtex import reference_to_bibtex
from .parsers import (
    parse_apa_citation as _parse_apa_citation_impl,
    parse_chicago_citation as _parse_chicago_citation_impl,
    parse_ieee_citation as _parse_ieee_citation_impl,
    parse_mla_citation as _parse_mla_citation_impl,
    parse_vancouver_citation as _parse_vancouver_citation_impl,
)
from .reference import Reference


class CitationParseError(ValueError):
    """Raised when a formatted citation string cannot be parsed."""


def parse_citation(style: str, text: str) -> Reference:
    """Parse a formatted citation string into a Reference."""
    normalized_style = style.strip().lower()
    parsers: dict[str, Callable[[str], Reference]] = {
        "apa": parse_apa_citation,
        "apa6": parse_apa_citation,
        "apa7": parse_apa_citation,
        "ieee": parse_ieee_citation,
        "chicago": parse_chicago_citation,
        "mla": parse_mla_citation,
        "vancouver": parse_vancouver_citation,
    }
    parser = parsers.get(normalized_style)
    if not parser:
        raise CitationParseError(
            "Unsupported style '{style}'. Supported: apa, apa7, ieee, chicago, mla, vancouver"
        )
    return parser(text)


def citation_to_bibtex(style: str, text: str) -> str:
    """Parse a formatted citation string and serialize it to BibTeX."""
    reference = parse_citation(style, text)
    return reference_to_bibtex(reference)


def parse_apa_citation(text: str) -> Reference:
    try:
        return _parse_apa_citation_impl(text)
    except ValueError as exc:
        raise CitationParseError(str(exc)) from exc


def parse_ieee_citation(text: str) -> Reference:
    try:
        return _parse_ieee_citation_impl(text)
    except ValueError as exc:
        raise CitationParseError(str(exc)) from exc


def parse_chicago_citation(text: str) -> Reference:
    try:
        return _parse_chicago_citation_impl(text)
    except ValueError as exc:
        raise CitationParseError(str(exc)) from exc


def parse_mla_citation(text: str) -> Reference:
    try:
        return _parse_mla_citation_impl(text)
    except ValueError as exc:
        raise CitationParseError(str(exc)) from exc


def parse_vancouver_citation(text: str) -> Reference:
    try:
        return _parse_vancouver_citation_impl(text)
    except ValueError as exc:
        raise CitationParseError(str(exc)) from exc


__all__ = [
    "CitationParseError",
    "parse_citation",
    "citation_to_bibtex",
    "parse_apa_citation",
    "parse_ieee_citation",
    "parse_chicago_citation",
    "parse_mla_citation",
    "parse_vancouver_citation",
]
