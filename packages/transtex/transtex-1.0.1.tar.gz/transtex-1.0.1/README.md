# TransTex (Python)

Reference conversion helpers for BibTeX plus APA 6th/7th, IEEE, MLA 9th, Chicago (author-date), and Vancouver styles.

## Features

- Parse BibTeX entries into structured `Reference` objects.
- Serialize references back to clean BibTeX.
- Convert formatted citations between supported styles.
- Handle common book/chapters and web sources in addition to journal articles.
- Provide runnable examples and unit tests.

## Project layout

```
src/        # Library source code (transtex package)
tests/      # Unit tests built with unittest
examples/   # Small runnable scripts demonstrating the API
```

## Getting started

Use [uv](https://github.com/astral-sh/uv) to run commands without mutating the base environment:

```bash
uv run python examples/format_from_bibtex.py
```

You can also round-trip formatted citations back into BibTeX:

```bash
uv run python examples/citation_to_bibtex.py
```

Convert citations across styles (APA → IEEE/Chicago/MLA, and back):

```bash
uv run python examples/convert_citation_styles.py
```

See book/web coverage:

```bash
uv run python examples/book_and_web_examples.py
```

## Usage

Format a `Reference` in multiple styles:

```python
from transtex import (
    Reference,
    format_apa,
    format_apa7,
    format_ieee,
    format_mla,
    format_chicago,
    format_vancouver,
    reference_to_bibtex,
)

ref = Reference(
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

print(format_apa(ref))
print(format_apa7(ref))
print(format_ieee(ref))
print(format_mla(ref))
print(format_chicago(ref))
print(format_vancouver(ref))

print(reference_to_bibtex(ref))
```

Parse a formatted citation back to BibTeX:

```python
from transtex import citation_to_bibtex

ieee_text = 'J. Doe and J. Smith, "Deep Learning for Everything," Journal of Omniscience, vol. 42, no. 7, pp. 1–10, 2020, doi: 10.1000/j.jo.2020.01.001.'
bibtex = citation_to_bibtex("ieee", ieee_text)
print(bibtex)
```

### Book / web example

```python
from transtex import Reference, format_apa, format_ieee

book_ref = Reference(
    entry_type="book",
    cite_key="turing1950",
    title="Computing Machinery and Intelligence",
    authors=["Alan M. Turing"],
    publisher="Oxford University Press",
    place="Oxford, UK",
    year="1950",
    edition="2nd ed.",
    pages="1-120",
)

web_ref = Reference(
    entry_type="misc",
    cite_key="ada1843",
    title="Sketch of the Analytical Engine",
    authors=["Ada Lovelace"],
    year="1843",
    url="https://example.org/analytical-engine",
    accessed_date="2024-02-10",
)

print(format_apa(book_ref))
print(format_ieee(web_ref))
```

## Running tests

```bash
uv run python -m unittest
```
