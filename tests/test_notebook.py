import pathlib

import pytest

from codelytics import Notebook


@pytest.fixture
def nb():
    return Notebook(
        pathlib.Path(__file__).parent / "data" / "project01" / "notebook01.ipynb"
    )


class TestInit:
    def test_invalid(self, nb):
        with pytest.raises(FileNotFoundError):
            Notebook(
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
        assert isinstance(code, str)
        assert "import pandas as pd" in code
        assert "sh = pd.DataFrame(data)" in code

    def test_md(self, nb):
        md = nb.extract(cell_type="markdown")
        assert isinstance(md, str)
        assert "# Test Notebook" in md
        assert "## Conclusion" in md
        assert "is complete" in md
