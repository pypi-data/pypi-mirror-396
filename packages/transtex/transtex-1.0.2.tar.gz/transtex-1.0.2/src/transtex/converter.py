"""Citation style conversion functions."""
from __future__ import annotations

from typing import Callable

from .formatters import (
    format_apa,
    format_apa7,
    format_chicago,
    format_ieee,
    format_mla,
    format_vancouver,
)
from .parsing import parse_citation
from .reference import Reference


class ConversionError(ValueError):
    """Raised when citation conversion fails."""


def format_reference(style: str, reference: Reference) -> str:
    """Format a Reference object into a citation string using the specified style.

    Args:
        style: Citation style (apa, apa6, apa7, ieee, mla, chicago, vancouver)
        reference: Reference object to format

    Returns:
        Formatted citation string

    Raises:
        ConversionError: If the style is not supported
    """
    normalized_style = style.strip().lower()
    formatters: dict[str, Callable[[Reference], str]] = {
        "apa": format_apa,
        "apa6": format_apa,
        "apa7": format_apa7,
        "ieee": format_ieee,
        "mla": format_mla,
        "chicago": format_chicago,
        "vancouver": format_vancouver,
    }

    formatter = formatters.get(normalized_style)
    if not formatter:
        supported = ", ".join(sorted(formatters.keys()))
        raise ConversionError(
            f"Unsupported style '{style}'. Supported styles: {supported}"
        )

    return formatter(reference)


def convert_citation(from_style: str, to_style: str, text: str) -> str:
    """Convert a citation from one style to another.

    This function parses a citation in the source style and reformats it
    into the target style. All supported citation styles can be converted
    to any other supported style.

    Args:
        from_style: Source citation style (apa, apa6, apa7, ieee, mla, chicago, vancouver)
        to_style: Target citation style (apa, apa6, apa7, ieee, mla, chicago, vancouver)
        text: Citation text in the source style

    Returns:
        Citation text formatted in the target style

    Raises:
        ConversionError: If parsing or formatting fails

    Examples:
        >>> apa_citation = 'Doe, J., & Smith, J. (2020). Deep learning. Journal, 42(7), 1–10.'
        >>> convert_citation('apa', 'ieee', apa_citation)
        'J. Doe and J. Smith, "Deep learning," Journal, vol. 42, no. 7, pp. 1–10, 2020.'
    """
    try:
        # Parse the citation into a Reference object
        reference = parse_citation(from_style, text)
    except Exception as exc:
        raise ConversionError(
            f"Failed to parse citation as {from_style} style: {exc}"
        ) from exc

    try:
        # Format the Reference into the target style
        return format_reference(to_style, reference)
    except Exception as exc:
        raise ConversionError(
            f"Failed to format citation as {to_style} style: {exc}"
        ) from exc


__all__ = [
    "ConversionError",
    "convert_citation",
    "format_reference",
]
