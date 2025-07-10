import pathlib

import pytest

import codelytics as cdl


@pytest.fixture(scope="module")
def pdf():
    return cdl.PDF(pathlib.Path(__file__).parent / "data" / "report.pdf")


class TestInit:
    def test_init(self, pdf):
        assert isinstance(pdf, cdl.PDF)
        assert pdf.path == pathlib.Path(__file__).parent / "data" / "report.pdf"

    def test_init_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            cdl.PDF("nonexistent.pdf")


class TestProperties:
    def test_n_pages(self, pdf):
        assert pdf.n_pages == 5

    def test_references_page(self, pdf):
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

    def test_gt(self, pdf):
        assert pdf.count_words(ignore_pages=[">5"]) == pdf.count_words()
        assert pdf.count_words(ignore_pages=[">4"]) == pdf.count_words(ignore_pages=[5])
