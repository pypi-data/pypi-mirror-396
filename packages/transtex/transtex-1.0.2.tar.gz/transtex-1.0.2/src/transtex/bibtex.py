"""Utility helpers for parsing and writing BibTeX entries."""
from __future__ import annotations

from typing import Dict, Tuple

from .reference import Reference


class BibTeXError(ValueError):
    """Raised when the library cannot parse a BibTeX entry."""


def parse_bibtex_entry(entry: str) -> Reference:
    """Parse a single BibTeX entry into a :class:`Reference`."""
    text = entry.strip()
    if not text:
        raise BibTeXError("Empty BibTeX entry")
    if not text.startswith("@"):
        raise BibTeXError("BibTeX entry must start with '@'")

    type_end = text.find("{")
    if type_end == -1:
        raise BibTeXError("Missing opening brace for entry")
    entry_type = text[1:type_end].strip()
    if not entry_type:
        raise BibTeXError("Entry type is missing")

    remainder = text[type_end + 1 :].strip()
    if not remainder.endswith("}"):
        raise BibTeXError("BibTeX entry must end with '}'")
    remainder = remainder[:-1].strip()
    if "," not in remainder:
        raise BibTeXError("BibTeX entry is missing fields")

    cite_key, field_blob = remainder.split(",", 1)
    cite_key = cite_key.strip()
    if not cite_key:
        raise BibTeXError("Entry cite key is missing")

    fields = _parse_fields(field_blob)
    return _reference_from_fields(entry_type, cite_key, fields)


def reference_to_bibtex(reference: Reference) -> str:
    """Serialize a :class:`Reference` back into a BibTeX entry."""
    fields = reference.merged_fields()
    order = [
        "author",
        "title",
        "journal",
        "booktitle",
        "publisher",
        "year",
        "volume",
        "number",
        "pages",
        "doi",
        "url",
    ]
    ordered_items = []
    for key in order:
        value = fields.pop(key, None)
        if value:
            ordered_items.append((key, value))
    for key in sorted(fields.keys()):
        ordered_items.append((key, fields[key]))

    if not ordered_items:
        body = ""
    else:
        field_lines = [f"  {key} = {{{value}}}" for key, value in ordered_items]
        body = ",\n".join(field_lines)
        body = "\n" + body + "\n"

    return f"@{reference.entry_type}{{{reference.cite_key},{body}}}"


def _parse_fields(blob: str) -> Dict[str, str]:
    fields: Dict[str, str] = {}
    idx = 0
    length = len(blob)
    while idx < length:
        while idx < length and blob[idx] in "\n\r\t ,":
            idx += 1
        if idx >= length:
            break

        start = idx
        while idx < length and (blob[idx].isalnum() or blob[idx] in "_-"):
            idx += 1
        name = blob[start:idx].lower()
        if not name:
            raise BibTeXError("Field name missing in BibTeX entry")

        while idx < length and blob[idx].isspace():
            idx += 1
        if idx >= length or blob[idx] != "=":
            raise BibTeXError(f"Field '{name}' misses '=' sign")
        idx += 1
        while idx < length and blob[idx].isspace():
            idx += 1
        value, idx = _consume_value(blob, idx)
        cleaned = _clean_value(value)
        fields[name] = cleaned

        while idx < length and blob[idx].isspace():
            idx += 1
        if idx < length and blob[idx] == ",":
            idx += 1
    return fields


def _consume_value(text: str, start: int) -> Tuple[str, int]:
    if start >= len(text):
        return "", start

    char = text[start]
    if char == "{":
        depth = 0
        idx = start + 1
        while idx < len(text):
            current = text[idx]
            if current == "{" :
                depth += 1
            elif current == "}":
                if depth == 0:
                    return text[start + 1 : idx], idx + 1
                depth -= 1
            idx += 1
        raise BibTeXError("Missing closing brace in value")

    if char == '"':
        idx = start + 1
        escaped = False
        while idx < len(text):
            current = text[idx]
            if current == '"' and not escaped:
                return text[start + 1 : idx], idx + 1
            escaped = current == "\\" and not escaped
            if current != "\\":
                escaped = False
            idx += 1
        raise BibTeXError("Missing closing quote in value")

    idx = start
    while idx < len(text) and text[idx] not in ",\n\r":
        idx += 1
    return text[start:idx].strip(), idx


def _clean_value(value: str) -> str:
    collapsed = " ".join(value.replace("\n", " ").split())
    return collapsed.strip()


def _reference_from_fields(entry_type: str, cite_key: str, fields: Dict[str, str]) -> Reference:
    authors_field = fields.get("author", "")
    authors = _split_authors(authors_field)
    normalized_entry = entry_type.lower()
    number_value = fields.get("number")
    issue = None
    report_number = None
    if number_value:
        if fields.get("journal") or normalized_entry in {"article", "inproceedings", "incollection"}:
            issue = number_value
        elif normalized_entry in {"techreport", "report"} or fields.get("institution"):
            report_number = number_value
        else:
            issue = number_value
    standard_keys = {
        "author",
        "title",
        "journal",
        "booktitle",
        "publisher",
        "address",
        "institution",
        "edition",
        "month",
        "day",
        "editor",
        "urldate",
        "medium",
        "year",
        "volume",
        "number",
        "pages",
        "doi",
        "url",
    }
    extra = {key: value for key, value in fields.items() if key not in standard_keys}
    return Reference(
        entry_type=entry_type,
        cite_key=cite_key,
        title=fields.get("title"),
        authors=authors,
        journal=fields.get("journal"),
        booktitle=fields.get("booktitle"),
        publisher=fields.get("publisher"),
        place=fields.get("address"),
        institution=fields.get("institution"),
        edition=fields.get("edition"),
        month=fields.get("month"),
        day=fields.get("day"),
        editors=_split_authors(fields.get("editor", "")),
        accessed_date=fields.get("urldate"),
        medium=fields.get("medium"),
        year=fields.get("year"),
        volume=fields.get("volume"),
        issue=issue,
        report_number=report_number,
        pages=fields.get("pages"),
        doi=fields.get("doi"),
        url=fields.get("url"),
        extra_fields=extra,
    )


def _split_authors(raw: str) -> list[str]:
    if not raw:
        return []
    return [author.strip() for author in raw.split(" and ") if author.strip()]


__all__ = ["BibTeXError", "parse_bibtex_entry", "reference_to_bibtex"]
