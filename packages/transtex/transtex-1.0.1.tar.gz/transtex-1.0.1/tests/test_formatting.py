import unittest

from transtex import (
    Reference,
    format_apa,
    format_apa7,
    format_chicago,
    format_ieee,
    format_mla,
    format_vancouver,
)


class FormattingTests(unittest.TestCase):
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

    def test_format_apa(self) -> None:
        formatted = format_apa(self.reference)
        expected = (
            "Doe, J., & Smith, J. (2020). Deep learning for everything. "
            "Journal of Omniscience, 42(7), 1–10. https://doi.org/10.1000/j.jo.2020.01.001"
        )
        self.assertEqual(formatted, expected)

    def test_format_apa_many_authors(self) -> None:
        authors = [
            "John Doe",
            "Jane Smith",
            "Alice Johnson",
            "Bob Lee",
            "Carol King",
            "Dan Park",
            "Eve Adams",
            "Frank Moore",
        ]
        reference = Reference(
            entry_type="article",
            cite_key="doe2020deep",
            title=self.reference.title,
            authors=authors,
            journal=self.reference.journal,
            year=self.reference.year,
            volume=self.reference.volume,
            issue=self.reference.issue,
            pages=self.reference.pages,
            doi=self.reference.doi,
        )
        formatted = format_apa(reference)
        expected_prefix = (
            "Doe, J., Smith, J., Johnson, A., Lee, B., King, C., Park, D., ... Moore, F. (2020)."
        )
        self.assertTrue(formatted.startswith(expected_prefix))

    def test_format_apa7(self) -> None:
        formatted = format_apa7(self.reference)
        expected = (
            "Doe, J., & Smith, J. (2020). Deep learning for everything. "
            "Journal of Omniscience, 42(7), 1–10. https://doi.org/10.1000/j.jo.2020.01.001"
        )
        self.assertEqual(formatted, expected)

    def test_format_ieee(self) -> None:
        formatted = format_ieee(self.reference)
        expected = (
            'J. Doe and J. Smith, "Deep Learning for Everything," Journal of Omniscience, '
            "vol. 42, no. 7, pp. 1–10, 2020, doi: 10.1000/j.jo.2020.01.001."
        )
        self.assertEqual(formatted, expected)

    def test_format_ieee_truncates_authors(self) -> None:
        reference = Reference(
            entry_type="article",
            cite_key="longauthors",
            title=self.reference.title,
            authors=[
                "John Doe",
                "Jane Smith",
                "Alice Johnson",
                "Bob Lee",
                "Carol King",
                "Dan Park",
                "Eve Adams",
            ],
            journal=self.reference.journal,
            year=self.reference.year,
            volume=self.reference.volume,
            issue=self.reference.issue,
            pages=self.reference.pages,
            doi=self.reference.doi,
        )
        formatted = format_ieee(reference)
        expected = (
            'J. Doe et al., "Deep Learning for Everything," Journal of Omniscience, '
            "vol. 42, no. 7, pp. 1–10, 2020, doi: 10.1000/j.jo.2020.01.001."
        )
        self.assertEqual(formatted, expected)

    def test_format_ieee_no_title(self) -> None:
        reference = Reference(
            entry_type="article",
            cite_key="notitle",
            title=None,
            authors=self.reference.authors,
            journal=self.reference.journal,
            year=self.reference.year,
            volume=self.reference.volume,
            issue=self.reference.issue,
            pages=self.reference.pages,
            doi=self.reference.doi,
        )
        formatted = format_ieee(reference)
        expected = (
            "J. Doe and J. Smith, Journal of Omniscience, vol. 42, no. 7, "
            "pp. 1–10, 2020, doi: 10.1000/j.jo.2020.01.001."
        )
        self.assertEqual(formatted, expected)

    def test_format_ieee_no_container(self) -> None:
        reference = Reference(
            entry_type="article",
            cite_key="nocontainer",
            title=self.reference.title,
            authors=self.reference.authors,
            year=self.reference.year,
            doi=self.reference.doi,
        )
        formatted = format_ieee(reference)
        expected = (
            'J. Doe and J. Smith, "Deep Learning for Everything," 2020, '
            "doi: 10.1000/j.jo.2020.01.001."
        )
        self.assertEqual(formatted, expected)

    def test_format_mla(self) -> None:
        formatted = format_mla(self.reference)
        expected = (
            'Doe, John, and Jane Smith. "Deep Learning for Everything." '
            "Journal of Omniscience, vol. 42, no. 7, 2020, pp. 1–10. "
            "https://doi.org/10.1000/j.jo.2020.01.001."
        )
        self.assertEqual(formatted, expected)

    def test_format_chicago(self) -> None:
        formatted = format_chicago(self.reference)
        expected = (
            'Doe, John, and Jane Smith. 2020. "Deep Learning for Everything." '
            "Journal of Omniscience 42 (7): 1–10. https://doi.org/10.1000/j.jo.2020.01.001."
        )
        self.assertEqual(formatted, expected)

    def test_format_vancouver(self) -> None:
        formatted = format_vancouver(self.reference)
        expected = (
            "Doe J, Smith J. Deep learning for everything. Journal of Omniscience. "
            "2020;42(7):1–10. doi:10.1000/j.jo.2020.01.001."
        )
        self.assertEqual(formatted, expected)


if __name__ == "__main__":
    unittest.main()
