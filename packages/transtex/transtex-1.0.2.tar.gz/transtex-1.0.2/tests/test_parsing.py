import unittest

from transtex import (
    CitationParseError,
    citation_to_bibtex,
    format_apa,
    format_chicago,
    format_ieee,
    format_mla,
    format_vancouver,
    parse_apa_citation,
    parse_citation,
    parse_ieee_citation,
    reference_to_bibtex,
)
from transtex.reference import Reference


class ParsingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.reference = Reference(
            entry_type="article",
            cite_key="doe2020deep",
            title="Deep Learning for Everything",
            authors=["John Doe", "Jane Smith"],
            journal="Journal of Omniscience",
            year="2020",
            volume="42",
            issue="7",
            pages="1-10",
            doi="10.1000/j.jo.2020.01.001",
        )

    def test_parse_apa_round_trip(self) -> None:
        citation = format_apa(self.reference)
        parsed = parse_apa_citation(citation)
        self.assertEqual(parsed.authors, ["Doe, J.", "Smith, J."])
        self.assertEqual(parsed.year, "2020")
        self.assertEqual(parsed.journal, "Journal of Omniscience")
        self.assertEqual(parsed.pages, "1–10")
        bibtex = reference_to_bibtex(parsed)
        self.assertIn("@article{doe2020deeplearningforeverything", bibtex)

    def test_parse_ieee_round_trip(self) -> None:
        citation = format_ieee(self.reference)
        parsed = parse_ieee_citation(citation)
        self.assertEqual(parsed.authors, ["J. Doe", "J. Smith"])
        self.assertEqual(parsed.title, self.reference.title)
        self.assertEqual(parsed.volume, "42")
        self.assertEqual(parsed.issue, "7")
        self.assertEqual(parsed.doi, "10.1000/j.jo.2020.01.001")
        bibtex = reference_to_bibtex(parsed)
        self.assertIn("@article{doe2020deeplearningforeverything", bibtex)

    def test_parse_dispatch(self) -> None:
        citation = format_apa(self.reference)
        parsed = parse_citation("apa", citation)
        self.assertEqual(parsed.year, "2020")

    def test_parse_chicago_round_trip(self) -> None:
        citation = format_chicago(self.reference)
        parsed = parse_citation("chicago", citation)
        self.assertEqual(parsed.title, self.reference.title)
        self.assertEqual(parsed.journal, self.reference.journal)
        self.assertEqual(parsed.volume, self.reference.volume)

    def test_parse_mla_round_trip(self) -> None:
        citation = format_mla(self.reference)
        parsed = parse_citation("mla", citation)
        self.assertEqual(parsed.title, self.reference.title)
        self.assertEqual(parsed.journal, self.reference.journal)
        self.assertEqual(parsed.volume, self.reference.volume)
        self.assertEqual(parsed.issue, self.reference.issue)

    def test_parse_vancouver_round_trip(self) -> None:
        citation = format_vancouver(self.reference)
        parsed = parse_citation("vancouver", citation)
        self.assertEqual(parsed.title.lower(), self.reference.title.lower())
        self.assertEqual(parsed.journal, self.reference.journal)
        self.assertEqual(parsed.volume, self.reference.volume)
        self.assertEqual(parsed.issue, self.reference.issue)

    def test_unknown_style(self) -> None:
        with self.assertRaises(CitationParseError):
            parse_citation("mla", "irrelevant")

    def test_citation_to_bibtex(self) -> None:
        citation = format_ieee(self.reference)
        bibtex = citation_to_bibtex("ieee", citation)
        self.assertIn("@article{doe2020deeplearningforeverything", bibtex)


if __name__ == "__main__":
    unittest.main()
