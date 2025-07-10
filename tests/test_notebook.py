import pathlib

import pytest

import codelytics as cdl


@pytest.fixture
def nb():
    return cdl.Notebook(
        pathlib.Path(__file__).parent / "data" / "project01" / "notebook01.ipynb"
    )


class TestInit:
    def test_invalid(self):
        with pytest.raises(FileNotFoundError):
            cdl.Notebook(
                pathlib.Path(__file__).parent / "data" / "project01" / "notebook01.txt"
            )


class TestNCells:
    def test_n_cells(self, nb):
        assert nb.n_cells() == 7

    def test_n_code_cells(self, nb):
        assert nb.n_cells(cell_type="code") == 3

    def test_n_markdown_cells(self, nb):
        assert nb.n_cells(cell_type="markdown") == 3

    def test_n_raw_cells(self, nb):
        assert nb.n_cells(cell_type="raw") == 1


class TestExtraction:
    def test_py(self, nb):
        code = nb.extract(cell_type="code")
        assert isinstance(code, cdl.Py)
        assert "import pandas as pd" in code.content
        assert "sh = pd.DataFrame(data)" in code.content

    def test_md(self, nb):
        md = nb.extract(cell_type="markdown")
        assert isinstance(md, cdl.TextAnalysis)
        assert len(md) == 1
        assert "# Test Notebook" in md[0]
        assert "analyse the data:" in md[0]
        assert "## Conclusion" in md[0]
        assert "is complete" in md[0]
