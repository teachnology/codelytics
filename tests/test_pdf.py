import pathlib

import pytest

from codelytics import PDF


@pytest.fixture(scope="module")
def pdf():
    return PDF(pathlib.Path(__file__).parent / "data" / "report.pdf")


def test_n_pages(pdf):
    assert pdf.n_pages == 5


def test_references_page(pdf):
    assert pdf.references_page() == 5


class TestCountWords:
    def test_ignore_all(self, pdf):
        assert pdf.count_words(ignore_pages=[">0"]) == 0
        assert pdf.count_words(ignore_pages=[1, 2, 3, 4, 5]) == 0

    def test_ignore_title_page(self, pdf):
        assert pdf.count_words(ignore_pages=[1]) < pdf.count_words()

    def test_ignore_last_page(self, pdf):
        assert pdf.count_words(ignore_pages=[5]) < pdf.count_words()

    def test_ignore_references(self, pdf):
        ignore_pages = [f">{pdf.references_page() - 1}"]
        assert pdf.count_words(ignore_pages=ignore_pages) < pdf.count_words()
