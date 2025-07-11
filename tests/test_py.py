import pathlib

import numpy as np
import pandas as pd
import pytest

import codelytics as cdl

PROJECT_DIR = pathlib.Path(__file__).parent / "data" / "project01"


@pytest.fixture
def simple():
    return cdl.Py(PROJECT_DIR / "simple.py")


@pytest.fixture
def counting():
    return cdl.Py(PROJECT_DIR / "counting.py")


@pytest.fixture
def empty():
    return cdl.Py("")


@pytest.fixture
def mccabe():
    return cdl.Py(PROJECT_DIR / "dir01" / "mccabe.py")


@pytest.fixture
def cognitive_complexity():
    return cdl.Py(PROJECT_DIR / "dir01" / "cognitive-complexity.py")


@pytest.fixture
def complex():
    return cdl.Py(PROJECT_DIR / "dir01" / "file02.py")


@pytest.fixture
def halstead():
    return cdl.Py(PROJECT_DIR / "dir01" / "halstead.py")


@pytest.fixture
def invalid_syntax():
    return cdl.Py(
        (PROJECT_DIR / "dir01" / "invalid-syntax" / "invalid-syntax.txt").read_text(
            encoding="utf-8"
        )
    )


@pytest.fixture
def user_defined_names():
    return cdl.Py(PROJECT_DIR / "dir01" / "user-defined-names.py")


class TestInitialization:
    def test_with_string(self):
        code = "x = 1"
        py = cdl.Py(code)
        assert py.content == code

    def test_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            cdl.Py(pathlib.Path("nonexistent_file_somewhere.py"))

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            cdl.Py(123)


class TestRadonAnalysis:
    def test_object(self, simple):
        analysis = simple.radon_analysis
        assert isinstance(analysis, tuple) and hasattr(analysis, "_fields")

    def test_loc(self, simple):
        assert simple.radon_analysis.loc == 25  # physical lines of code

    def test_lloc(self, simple):
        # Multiline docstrings count as one line.
        # Statements that span multiple lines count as one line.
        assert simple.radon_analysis.lloc == 5

    def test_sloc(self, simple):
        # Comments and docstrings are excluded.
        # Multiline statements are counted as multiple lines.
        assert simple.radon_analysis.sloc == 7

    def test_comments(self, simple):
        # Block and inline comments are counted.
        assert simple.radon_analysis.comments == 5

    def test_blank(self, simple):
        # Blank lines inside docstrings are counted.
        assert simple.radon_analysis.blank == 8

    def test_multi(self, simple):
        # Number of lines in docstrings
        # Blank lines inside docstrings are excluded.
        # """ is counted if it is on a separate line.
        assert simple.radon_analysis.multi == 7

    def test_radon_analysis_empty(self, empty):
        analysis = empty.radon_analysis
        assert all(getattr(analysis, attr) == 0 for attr in analysis._fields)

    def test_comparisons(self, simple):
        assert simple.lloc < simple.radon_analysis.lloc
        assert simple.radon_analysis.lloc < simple.radon_analysis.sloc
        assert simple.radon_analysis.sloc < simple.radon_analysis.loc


class TestLLOC:
    def test_simple(self, simple):
        assert simple.lloc == 4

    def test_empty(self, empty):
        assert empty.lloc == 0


class TestNChar:
    def test_simple(self, simple):
        assert 390 < simple.n_char < 400

    def test_empty(self, empty):
        assert empty.n_char == 0


class TestNFunctions:
    def test_simple(self, simple):
        assert simple.n_functions == 1

    def test_counting(self, counting):
        assert counting.n_functions == 11

    def test_empty(self, empty):
        assert empty.n_functions == 0


class TestNClasses:
    def test_simple(self, simple):
        assert simple.n_classes == 0

    def test_counting(self, counting):
        assert counting.n_classes == 2

    def test_empty(self, empty):
        assert empty.n_classes == 0


class TestNImports:
    def test_simple(self, simple):
        assert simple.n_imports == 0

    def test_counting(self, counting):
        assert counting.n_imports == 5  # from math import sqrt is hidden

    def test_empty(self, empty):
        assert empty.n_imports == 0


class TestNImportedModules:
    def test_simple(self, simple):
        assert simple.n_imported_modules == 0

    def test_counting(self, counting):
        assert counting.n_imported_modules == 4  # math is imported twice

    def test_empty(self, empty):
        assert empty.n_imported_modules == 0


class TestIsValidSyntax:
    def test_valid_syntax(self, simple):
        assert simple.is_valid_syntax

    def test_invalid_syntax(self, invalid_syntax):
        assert not invalid_syntax.is_valid_syntax

    def test_empty(self, empty):
        assert empty.is_valid_syntax is True  # Empty files are considered valid


class TestMcCabe:
    def test_simple(self, simple):
        # 1 for the if statement, +1 by default
        assert simple.mccabe(total=True) == 1 + 1

        # One function with 1 complexity (+1 by default)
        assert simple.mccabe(total=False, use_median=False) == 1
        assert simple.mccabe(total=False, use_median=True) == 1

    def test_mccabe(self, mccabe):
        assert mccabe.mccabe(total=True) == (0 + 1 + 2 + 3 + 3 + 3) + 1

        per_function = [1, 2, 3, 4, 4]

        assert np.isclose(
            mccabe.mccabe(total=False, use_median=False),
            pd.Series(per_function).mean(),
        )

        assert np.isclose(
            mccabe.mccabe(total=False, use_median=True),
            pd.Series(per_function).median(),
        )

    def test_empty(self, empty):
        assert empty.mccabe(total=True) == 0 + 1
        assert empty.mccabe(total=False, use_median=False) == 0
        assert empty.mccabe(total=False, use_median=True) == 0


class TestCognitiveComplexity:
    def test_simple(self, simple):
        assert simple.cognitive_complexity(total=True) == 1
        assert simple.cognitive_complexity(total=False, use_median=False) == 0
        assert simple.cognitive_complexity(total=False, use_median=True) == 0

    def test_cognitive_complexity(self, cognitive_complexity):
        per_function = [0, 1, 6, 0, 6]
        assert (
            cognitive_complexity.cognitive_complexity(total=True)
            == sum(per_function) + 1
        )

        assert np.isclose(
            cognitive_complexity.cognitive_complexity(total=False, use_median=False),
            pd.Series(per_function).mean(),
        )
        assert np.isclose(
            cognitive_complexity.cognitive_complexity(total=False, use_median=True),
            pd.Series(per_function).median(),
        )

    def test_empty(self, empty):
        assert empty.cognitive_complexity(total=False) == 0
        assert empty.cognitive_complexity(total=True) == 0


class TestHalstead:
    def test_simple(self, simple):
        assert simple.halstead(total=False).eq(0).all()

    def test_halstead(self, halstead):
        metrics = halstead.halstead(total=True)

        assert metrics.mean() > 0.0

        # vocabulary = 3 + 3 + 5 + 7
        # assert np.isclose(metrics.loc["vocabulary"], vocabulary)

        # not sure why +1 is added to length
        length = 3 + 3 + 6 + 8 + 1
        assert np.isclose(metrics.loc["length"], length)

    def test_halstead_mean(self, halstead):
        metrics = halstead.halstead(total=False, use_median=False)

        vocabulary = (3 + 3 + 5) / 3
        assert np.isclose(metrics.loc["vocabulary"], vocabulary)

        length = (3 + 3 + 6) / 3
        assert np.isclose(metrics.loc["length"], length)

        volume = (3 * np.log2(3) + 3 * np.log2(3) + 6 * np.log2(5)) / 3
        assert np.isclose(metrics.loc["volume"], volume)

        difficulty = (1 / 2 * 2 / 2 + 1 / 2 * 2 / 2 + 2 / 2 * 4 / 3) / 3
        assert np.isclose(metrics.loc["difficulty"], difficulty)

        assert metrics.loc["effort"] >= 0

    def test_halstead_median(self, halstead):
        metrics = halstead.halstead(total=False, use_median=True)

        vocabulary = np.median([3, 3, 5])
        assert np.isclose(metrics.loc["vocabulary"], vocabulary)

        length = np.median([3, 3, 6])
        assert np.isclose(metrics.loc["length"], length)

        volume = np.median([3 * np.log2(3), 3 * np.log2(3), 6 * np.log2(5)])
        assert np.isclose(metrics.loc["volume"], volume)

        difficulty = np.median([1 / 2 * 2 / 2, 1 / 2 * 2 / 2, 2 / 2 * 4 / 3])
        assert np.isclose(metrics.loc["difficulty"], difficulty)

        assert metrics.loc["effort"] >= 0

    def test_empty(self, empty):
        assert empty.halstead(total=False).mean() == 0.0


class TestEdgeCases:
    def test_syntax_error_handling(self, invalid_syntax):
        assert "x =+ 5" in invalid_syntax.content
        assert invalid_syntax.radon_analysis is None
        assert invalid_syntax.lloc is None
        assert invalid_syntax.n_char > 100
        assert invalid_syntax.n_functions is None
        assert invalid_syntax.n_classes is None
        assert invalid_syntax.n_imports is None
        assert invalid_syntax.n_imported_modules is None
        assert invalid_syntax.mccabe(total=True) is None
        assert not invalid_syntax.is_valid_syntax
        assert invalid_syntax.cognitive_complexity(total=True) is None
        assert invalid_syntax.halstead(total=False).isna().all()
        assert invalid_syntax.user_defined_names.names == []
        assert invalid_syntax.comments.texts == []
        assert invalid_syntax.docstrings.texts == []


class TestUserDefinedNames:
    def test_simple(self, simple):
        assert all(
            name in simple.user_defined_names.names for name in ["hello", "name"]
        )

    def test_user_defined_names(self, user_defined_names):
        names = user_defined_names.user_defined_names.names

        expected = [
            "counter",
            "total_sum",
            "n",
            "process_data",
            "data",
            "results",
            "item",
            "value",
            "squared",
            "x",
            "f",
            "e",
            "Calculator",
            "name",
            "add",
            "result",
            "history",
            "y",
        ]
        assert all(name in names for name in expected)

    def test_empty(self, empty):
        assert empty.user_defined_names.names == []


class TestComments:
    def test_simple(self, simple):
        comments = simple.comments
        assert len(comments) == 5
        assert comments[0] == "Block comment 1"
        assert comments[2] == "inline comment"
        assert comments[-1] == "Footer comment 1"

    def test_empty(self, empty):
        comments = empty.comments
        assert len(comments) == 0


class TestDocstrings:
    def test_simple(self, simple):
        assert len(simple.docstrings) == 1

    def test_halstead(self, halstead):
        assert len(halstead.docstrings) == 0

    def test_empty(self, empty):
        assert len(empty.docstrings) == 0

    def test_counting(self, counting):
        docstrings = counting.docstrings

        assert len(docstrings) == 9
        assert docstrings[0] == "Calculate basic statistics for a dataset."
        assert "Parameters" in docstrings[-1]
