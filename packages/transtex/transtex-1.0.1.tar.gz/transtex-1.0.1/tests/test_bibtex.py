import unittest

from transtex import BibTeXError, parse_bibtex_entry, reference_to_bibtex


SAMPLE_ENTRY = """@article{doe2020deep,
  author = {John Doe and Jane Smith},
  title = {Deep Learning for Everything},
  journal = {Journal of Omniscience},
  year = {2020},
  volume = {42},
  number = {7},
  pages = {1-10},
  doi = {10.1000/j.jo.2020.01.001},
  url = {https://example.com/article}
}"""


class BibTeXParsingTests(unittest.TestCase):
    def test_parse_entry(self) -> None:
        reference = parse_bibtex_entry(SAMPLE_ENTRY)
        self.assertEqual(reference.entry_type, "article")
        self.assertEqual(reference.cite_key, "doe2020deep")
        self.assertEqual(reference.title, "Deep Learning for Everything")
        self.assertEqual(reference.journal, "Journal of Omniscience")
        self.assertEqual(reference.year, "2020")
        self.assertEqual(reference.volume, "42")
        self.assertEqual(reference.issue, "7")
        self.assertEqual(reference.pages, "1-10")
        self.assertEqual(reference.doi, "10.1000/j.jo.2020.01.001")
        self.assertEqual(
            reference.authors,
            ["John Doe", "Jane Smith"],
        )

    def test_round_trip_serialization(self) -> None:
        reference = parse_bibtex_entry(SAMPLE_ENTRY)
        serialized = reference_to_bibtex(reference)
        reparsed = parse_bibtex_entry(serialized)
        self.assertEqual(reparsed.title, reference.title)
        self.assertEqual(reparsed.journal, reference.journal)
        self.assertEqual(reparsed.authors, reference.authors)

    def test_rejects_invalid_entries(self) -> None:
        with self.assertRaises(BibTeXError):
            parse_bibtex_entry("invalid")


if __name__ == "__main__":
    unittest.main()
