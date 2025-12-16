"""Core data structures used by the TransTex library."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Reference:
    """Represents a normalized scholarly reference entry."""

    entry_type: str
    cite_key: str
    title: Optional[str] = None
    authors: List[str] = field(default_factory=list)
    journal: Optional[str] = None
    booktitle: Optional[str] = None
    publisher: Optional[str] = None
    place: Optional[str] = None
    institution: Optional[str] = None
    edition: Optional[str] = None
    report_number: Optional[str] = None
    event_title: Optional[str] = None
    event_location: Optional[str] = None
    month: Optional[str] = None
    day: Optional[str] = None
    editors: List[str] = field(default_factory=list)
    accessed_date: Optional[str] = None
    medium: Optional[str] = None
    year: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    extra_fields: Dict[str, str] = field(default_factory=dict)

    def normalized_authors(self) -> List[str]:
        """Return authors stripped of surrounding whitespace."""
        return [author.strip() for author in self.authors if author.strip()]

    def primary_container(self) -> Optional[str]:
        """Return the journal/booktitle/publisher used for formatting."""
        return self.journal or self.booktitle or self.publisher

    def merged_fields(self) -> Dict[str, str]:
        """Return a dict describing the entry with BibTeX friendly keys."""
        fields: Dict[str, str] = {}
        if self.normalized_authors():
            fields["author"] = " and ".join(self.normalized_authors())
        if self.title:
            fields["title"] = self.title
        if self.journal:
            fields["journal"] = self.journal
        if self.booktitle:
            fields["booktitle"] = self.booktitle
        if self.publisher:
            fields["publisher"] = self.publisher
        if self.place:
            fields["address"] = self.place
        if self.institution:
            fields["institution"] = self.institution
        if self.edition:
            fields["edition"] = self.edition
        if self.report_number:
            fields["number"] = self.report_number
        if self.event_title:
            fields["eventtitle"] = self.event_title
        if self.event_location:
            fields["eventlocation"] = self.event_location
        if self.month:
            fields["month"] = self.month
        if self.day:
            fields["day"] = self.day
        if self.editors:
            fields["editor"] = " and ".join(self.editors)
        if self.accessed_date:
            fields["urldate"] = self.accessed_date
        if self.medium:
            fields["medium"] = self.medium
        if self.year:
            fields["year"] = self.year
        if self.volume:
            fields["volume"] = self.volume
        if self.issue:
            fields["number"] = self.issue
        if self.pages:
            fields["pages"] = self.pages
        if self.doi:
            fields["doi"] = self.doi
        if self.url:
            fields["url"] = self.url

        for key, value in self.extra_fields.items():
            if key not in fields:
                fields[key] = value
        return fields


__all__ = ["Reference"]
