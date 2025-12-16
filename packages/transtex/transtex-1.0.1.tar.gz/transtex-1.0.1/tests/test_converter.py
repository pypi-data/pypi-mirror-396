import unittest

from transtex import ConversionError, Reference, convert_citation, format_reference


class FormatReferenceTests(unittest.TestCase):
    """Test format_reference function with various styles."""

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

    def test_format_reference_apa(self) -> None:
        result = format_reference("apa", self.reference)
        expected = (
            "Doe, J., & Smith, J. (2020). Deep learning for everything. "
            "Journal of Omniscience, 42(7), 1–10. https://doi.org/10.1000/j.jo.2020.01.001"
        )
        self.assertEqual(result, expected)

    def test_format_reference_apa6(self) -> None:
        result = format_reference("apa6", self.reference)
        expected = (
            "Doe, J., & Smith, J. (2020). Deep learning for everything. "
            "Journal of Omniscience, 42(7), 1–10. https://doi.org/10.1000/j.jo.2020.01.001"
        )
        self.assertEqual(result, expected)

    def test_format_reference_apa7(self) -> None:
        result = format_reference("apa7", self.reference)
        expected = (
            "Doe, J., & Smith, J. (2020). Deep learning for everything. "
            "Journal of Omniscience, 42(7), 1–10. https://doi.org/10.1000/j.jo.2020.01.001"
        )
        self.assertEqual(result, expected)

    def test_format_reference_ieee(self) -> None:
        result = format_reference("ieee", self.reference)
        expected = (
            'J. Doe and J. Smith, "Deep Learning for Everything," Journal of Omniscience, '
            "vol. 42, no. 7, pp. 1–10, 2020, doi: 10.1000/j.jo.2020.01.001."
        )
        self.assertEqual(result, expected)

    def test_format_reference_mla(self) -> None:
        result = format_reference("mla", self.reference)
        expected = (
            'Doe, John, and Jane Smith. "Deep Learning for Everything." '
            "Journal of Omniscience, vol. 42, no. 7, 2020, pp. 1–10. "
            "https://doi.org/10.1000/j.jo.2020.01.001."
        )
        self.assertEqual(result, expected)

    def test_format_reference_chicago(self) -> None:
        result = format_reference("chicago", self.reference)
        expected = (
            'Doe, John, and Jane Smith. 2020. "Deep Learning for Everything." '
            "Journal of Omniscience 42 (7): 1–10. https://doi.org/10.1000/j.jo.2020.01.001."
        )
        self.assertEqual(result, expected)

    def test_format_reference_vancouver(self) -> None:
        result = format_reference("vancouver", self.reference)
        expected = (
            "Doe J, Smith J. Deep learning for everything. Journal of Omniscience. "
            "2020;42(7):1–10. doi:10.1000/j.jo.2020.01.001."
        )
        self.assertEqual(result, expected)

    def test_format_reference_case_insensitive(self) -> None:
        result1 = format_reference("APA", self.reference)
        result2 = format_reference("apa", self.reference)
        self.assertEqual(result1, result2)

    def test_format_reference_unsupported_style(self) -> None:
        with self.assertRaises(ConversionError) as ctx:
            format_reference("unsupported", self.reference)
        self.assertIn("Unsupported style", str(ctx.exception))


class ConvertCitationTests(unittest.TestCase):
    """Test convert_citation function with various style conversions."""

    def setUp(self) -> None:
        # Sample citations in different styles for the same reference
        self.apa_citation = (
            "Doe, J., & Smith, J. (2020). Deep learning for everything. "
            "Journal of Omniscience, 42(7), 1–10. https://doi.org/10.1000/j.jo.2020.01.001"
        )
        self.ieee_citation = (
            'J. Doe and J. Smith, "Deep Learning for Everything," Journal of Omniscience, '
            "vol. 42, no. 7, pp. 1–10, 2020, doi: 10.1000/j.jo.2020.01.001."
        )
        self.mla_citation = (
            'Doe, J., and J. Smith. "Deep Learning for Everything." '
            "Journal of Omniscience, vol. 42, no. 7, 2020, pp. 1–10. "
            "https://doi.org/10.1000/j.jo.2020.01.001."
        )
        self.chicago_citation = (
            'Doe, J., and J. Smith. 2020. "Deep Learning for Everything." '
            "Journal of Omniscience 42 (7): 1–10. https://doi.org/10.1000/j.jo.2020.01.001."
        )
        self.vancouver_citation = (
            "Doe J, Smith J. Deep learning for everything. Journal of Omniscience. "
            "2020;42(7):1–10. doi:10.1000/j.jo.2020.01.001."
        )
        self.apa7_citation = (
            "Doe, J., & Smith, J. (2020). Deep learning for everything. "
            "Journal of Omniscience, 42(7), 1–10. https://doi.org/10.1000/j.jo.2020.01.001"
        )

    def test_convert_apa_to_ieee(self) -> None:
        result = convert_citation("apa", "ieee", self.apa_citation)
        self.assertEqual(result, self.ieee_citation)

    def test_convert_apa_to_mla(self) -> None:
        result = convert_citation("apa", "mla", self.apa_citation)
        self.assertEqual(result, self.mla_citation)

    def test_convert_apa_to_chicago(self) -> None:
        result = convert_citation("apa", "chicago", self.apa_citation)
        self.assertEqual(result, self.chicago_citation)

    def test_convert_apa_to_vancouver(self) -> None:
        result = convert_citation("apa", "vancouver", self.apa_citation)
        self.assertEqual(result, self.vancouver_citation)

    def test_convert_apa_to_apa7(self) -> None:
        result = convert_citation("apa", "apa7", self.apa_citation)
        self.assertEqual(result, self.apa7_citation)

    def test_convert_ieee_to_apa(self) -> None:
        result = convert_citation("ieee", "apa", self.ieee_citation)
        self.assertEqual(result, self.apa_citation)

    def test_convert_ieee_to_mla(self) -> None:
        result = convert_citation("ieee", "mla", self.ieee_citation)
        self.assertEqual(result, self.mla_citation)

    def test_convert_ieee_to_chicago(self) -> None:
        result = convert_citation("ieee", "chicago", self.ieee_citation)
        self.assertEqual(result, self.chicago_citation)

    def test_convert_ieee_to_vancouver(self) -> None:
        result = convert_citation("ieee", "vancouver", self.ieee_citation)
        self.assertEqual(result, self.vancouver_citation)

    def test_convert_ieee_to_apa7(self) -> None:
        result = convert_citation("ieee", "apa7", self.ieee_citation)
        self.assertEqual(result, self.apa7_citation)

    def test_convert_mla_to_apa(self) -> None:
        result = convert_citation("mla", "apa", self.mla_citation)
        self.assertEqual(result, self.apa_citation)

    def test_convert_mla_to_ieee(self) -> None:
        result = convert_citation("mla", "ieee", self.mla_citation)
        self.assertEqual(result, self.ieee_citation)

    def test_convert_mla_to_chicago(self) -> None:
        result = convert_citation("mla", "chicago", self.mla_citation)
        self.assertEqual(result, self.chicago_citation)

    def test_convert_mla_to_vancouver(self) -> None:
        result = convert_citation("mla", "vancouver", self.mla_citation)
        self.assertEqual(result, self.vancouver_citation)

    def test_convert_mla_to_apa7(self) -> None:
        result = convert_citation("mla", "apa7", self.mla_citation)
        self.assertEqual(result, self.apa7_citation)

    def test_convert_chicago_to_apa(self) -> None:
        result = convert_citation("chicago", "apa", self.chicago_citation)
        self.assertEqual(result, self.apa_citation)

    def test_convert_chicago_to_ieee(self) -> None:
        result = convert_citation("chicago", "ieee", self.chicago_citation)
        self.assertEqual(result, self.ieee_citation)

    def test_convert_chicago_to_mla(self) -> None:
        result = convert_citation("chicago", "mla", self.chicago_citation)
        self.assertEqual(result, self.mla_citation)

    def test_convert_chicago_to_vancouver(self) -> None:
        result = convert_citation("chicago", "vancouver", self.chicago_citation)
        self.assertEqual(result, self.vancouver_citation)

    def test_convert_chicago_to_apa7(self) -> None:
        result = convert_citation("chicago", "apa7", self.chicago_citation)
        self.assertEqual(result, self.apa7_citation)

    def test_convert_vancouver_to_apa(self) -> None:
        result = convert_citation("vancouver", "apa", self.vancouver_citation)
        self.assertEqual(result, self.apa_citation)

    def test_convert_vancouver_to_ieee(self) -> None:
        result = convert_citation("vancouver", "ieee", self.vancouver_citation)
        self.assertEqual(result, self.ieee_citation)

    def test_convert_vancouver_to_mla(self) -> None:
        result = convert_citation("vancouver", "mla", self.vancouver_citation)
        self.assertEqual(result, self.mla_citation)

    def test_convert_vancouver_to_chicago(self) -> None:
        result = convert_citation("vancouver", "chicago", self.vancouver_citation)
        self.assertEqual(result, self.chicago_citation)

    def test_convert_vancouver_to_apa7(self) -> None:
        result = convert_citation("vancouver", "apa7", self.vancouver_citation)
        self.assertEqual(result, self.apa7_citation)

    def test_convert_apa7_to_apa(self) -> None:
        result = convert_citation("apa7", "apa", self.apa7_citation)
        self.assertEqual(result, self.apa_citation)

    def test_convert_apa7_to_ieee(self) -> None:
        result = convert_citation("apa7", "ieee", self.apa7_citation)
        self.assertEqual(result, self.ieee_citation)

    def test_convert_apa7_to_mla(self) -> None:
        result = convert_citation("apa7", "mla", self.apa7_citation)
        self.assertEqual(result, self.mla_citation)

    def test_convert_apa7_to_chicago(self) -> None:
        result = convert_citation("apa7", "chicago", self.apa7_citation)
        self.assertEqual(result, self.chicago_citation)

    def test_convert_apa7_to_vancouver(self) -> None:
        result = convert_citation("apa7", "vancouver", self.apa7_citation)
        self.assertEqual(result, self.vancouver_citation)

    def test_convert_same_style(self) -> None:
        # Converting to same style should return normalized output
        result = convert_citation("apa", "apa", self.apa_citation)
        self.assertEqual(result, self.apa_citation)

    def test_convert_invalid_source_style(self) -> None:
        with self.assertRaises(ConversionError) as ctx:
            convert_citation("invalid", "apa", self.apa_citation)
        self.assertIn("Failed to parse", str(ctx.exception))

    def test_convert_invalid_target_style(self) -> None:
        with self.assertRaises(ConversionError) as ctx:
            convert_citation("apa", "invalid", self.apa_citation)
        self.assertIn("Failed to format", str(ctx.exception))

    def test_convert_case_insensitive_styles(self) -> None:
        result1 = convert_citation("APA", "IEEE", self.apa_citation)
        result2 = convert_citation("apa", "ieee", self.apa_citation)
        self.assertEqual(result1, result2)

    def test_convert_with_book_reference(self) -> None:
        # Test with a book citation
        apa_book = (
            "Smith, J. (2021). The Art of Programming. "
            "Tech Publishing House. https://doi.org/10.1000/book.2021"
        )
        result = convert_citation("apa", "ieee", apa_book)
        # Verify it doesn't crash and produces some output
        self.assertIn("Smith", result)
        self.assertIn("2021", result)
        self.assertIn("The Art of Programming", result)

    def test_convert_roundtrip(self) -> None:
        # Test that converting APA -> IEEE -> APA produces consistent result
        ieee_converted = convert_citation("apa", "ieee", self.apa_citation)
        apa_reconverted = convert_citation("ieee", "apa", ieee_converted)
        self.assertEqual(apa_reconverted, self.apa_citation)


class ConversionEdgeCasesTests(unittest.TestCase):
    """Test edge cases and error handling in conversion."""

    def test_convert_with_minimal_information(self) -> None:
        # Citation with minimal information
        minimal_apa = "Doe, J. (2020). Title."
        result = convert_citation("apa", "ieee", minimal_apa)
        self.assertIn("Doe", result)
        self.assertIn("2020", result)
        self.assertIn("Title", result)

    def test_convert_with_many_authors(self) -> None:
        # Test with many authors - different styles handle this differently
        many_authors_apa = (
            "Doe, J., Smith, J., Johnson, A., Lee, B., King, C., Park, D., ... Moore, F. (2020). "
            "Title. Journal, 42(7), 1–10."
        )
        # Should not raise an error
        result = convert_citation("apa", "ieee", many_authors_apa)
        self.assertIn("Doe", result)
        self.assertIn("Title", result)

    def test_format_reference_with_empty_fields(self) -> None:
        # Reference with some empty fields
        from transtex import Reference

        sparse_ref = Reference(
            entry_type="article",
            cite_key="test",
            title="Test Title",
            authors=["Author Name"],
            year="2020",
        )
        # Should format without errors
        result = format_reference("apa", sparse_ref)
        self.assertIn("Author Name", result)
        self.assertIn("test title", result.lower())
        self.assertIn("2020", result)


if __name__ == "__main__":
    unittest.main()
