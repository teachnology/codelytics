import pathlib

import pytest

import codelytics as cdl

PROJECT_DIR = pathlib.Path(__file__).parent / "data" / "project01"


@pytest.fixture
def nb():
    return cdl.Notebook(PROJECT_DIR / "valid-notebook.ipynb")


@pytest.fixture
def invalid_nb():
    return cdl.Notebook(
        PROJECT_DIR / "dir01" / "invalid-syntax" / "invalid-notebook.ipynb"
    )


class TestInit:
    def test_invalid(self):
        with pytest.raises(FileNotFoundError):
            cdl.Notebook(PROJECT_DIR / "notebook01.txt")


class TestNCells:
    def test_n_cells(self, nb):
        assert nb.n_cells() == 7

    def test_n_code_cells(self, nb):
        assert nb.n_cells(cell_type="code") == 3

    def test_n_markdown_cells(self, nb):
        assert nb.n_cells(cell_type="markdown") == 3

    def test_n_raw_cells(self, nb):
        assert nb.n_cells(cell_type="raw") == 1


class TestExtractionValid:
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


class TestExtractionInvalid:
    def test_py(self, invalid_nb):
        code = invalid_nb.extract(cell_type="code")
        assert isinstance(code, cdl.Py)
        assert "import numpy as np" not in code.content
        assert "to_array(lst)" not in code.content
        assert "a + b" not in code.content
        assert "def valid_syntax():" in code.content

    def test_md(self, invalid_nb):
        md = invalid_nb.extract(cell_type="markdown")
        assert isinstance(md, cdl.TextAnalysis)
        assert len(md) == 1
        assert "# Invalid analysis - do not run this notebook" in md[0]
        assert "## Another wrong cell" in md[0]
        assert "Wrong indentations in the cell below:" in md[0]
        assert "Finally, one correct cell:" in md[0]
