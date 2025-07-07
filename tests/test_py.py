import pathlib

import numpy as np
import pytest

from codelytics import Py


@pytest.fixture
def simple():
    return Py(pathlib.Path(__file__).parent / "data" / "project01" / "file01.py")


@pytest.fixture
def complex():
    return Py(
        pathlib.Path(__file__).parent / "data" / "project01" / "dir1" / "file02.py"
    )


@pytest.fixture
def imports():
    return Py(
        pathlib.Path(__file__).parent / "data" / "project01" / "dir1" / "file03.py"
    )


@pytest.fixture
def cc():
    return Py(
        pathlib.Path(__file__).parent / "data" / "project01" / "dir1" / "file04.py"
    )


@pytest.fixture
def cogc():
    return Py(
        pathlib.Path(__file__).parent / "data" / "project01" / "dir1" / "file05.py"
    )


@pytest.fixture
def halstead():
    return Py(
        pathlib.Path(__file__).parent / "data" / "project01" / "dir1" / "file06.py"
    )


@pytest.fixture
def user_defined_names():
    return Py(
        pathlib.Path(__file__).parent / "data" / "project01" / "dir1" / "file07.py"
    )


@pytest.fixture
def comment_only():
    code = """# Just a comment
# Another comment

# Third comment
"""
    return Py(code)


@pytest.fixture
def mixed_docstrings():
    code = """
# Header comment
def func():
    '''Docstring here'''
    x = 1  # inline comment

    # Another comment
    return x

# Footer comment
"""
    return Py(code)


@pytest.fixture
def unicode_content():
    code = """# Comment with unicode: café
def greet():
    return "Hello 世界"
"""
    return Py(code)


@pytest.fixture
def multiline_strings():
    code = '''MULTILINE = """
This is a multiline string
that spans several lines
"""

def func():
    """This is a docstring"""
    return MULTILINE
'''
    return Py(code)


@pytest.fixture
def whitespace_only():
    code = "   \n\t\n   \n"
    return Py(code)


@pytest.fixture
def empty():
    return Py("")


@pytest.fixture
def syntax_error():
    code = "def invalid syntax here"
    return Py(code)


class TestInitialization:
    def test_with_string(self):
        code = "x = 1"
        py = Py(code)
        assert py.content == code

    def test_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            Py(pathlib.Path("nonexistent_file_somewhere.py"))

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            Py(123)


class TestLoc:
    def test_simple(self, simple):
        assert simple.loc() == 5

    def test_complex(self, complex):
        assert complex.loc() == 33

    def test_empty(self, empty):
        assert empty.loc() == 0


class TestLloc:
    def test_simple(self, simple):
        assert simple.lloc() == 2

    def test_complex(self, complex):
        assert complex.lloc() == 16  # includes docstings but not comments
        assert complex.lloc() < complex.loc()

    def test_empty(self, empty):
        assert empty.lloc() == 0


class TestSloc:
    def test_simple(self, simple):
        assert simple.sloc() == 2

    def test_complex(self, complex):
        # excludes docstrings and comments but includes multiline statements.
        assert complex.sloc() == 18
        assert complex.sloc() < complex.loc()

    def test_comment_only(self, comment_only):
        assert comment_only.sloc() == 0

    def test_excludes_docstrings(self, mixed_docstrings):
        assert mixed_docstrings.sloc() == 3

    def test_empty(self, empty):
        assert empty.sloc() == 0


class TestNChar:
    def test_simple(self, simple):
        assert simple.n_char() < 70

    def test_complex(self, complex):
        assert complex.n_char() > 100

    def test_empty(self, empty):
        assert empty.n_char() == 0


class TestEdgeCases:
    def test_syntax_error_handling(self, syntax_error):
        assert syntax_error.loc() == 1
        assert syntax_error.lloc() == 1
        assert syntax_error.sloc() == 1
        assert syntax_error.n_char() == len("def invalid syntax here")

    def test_unicode_content(self, unicode_content):
        assert unicode_content.n_char() > 50
        assert unicode_content.loc() > 0

    def test_multiline_strings(self, multiline_strings):
        assert multiline_strings.loc() == 8
        assert multiline_strings.lloc() == 4
        assert multiline_strings.sloc() == 6

    def test_only_whitespace(self, whitespace_only):
        assert whitespace_only.loc() == 3
        assert whitespace_only.sloc() == 0
        assert whitespace_only.lloc() == 0


class TestNFunctions:
    def test_simple(self, simple):
        assert simple.n_functions() == 1

    def test_complex(self, complex):
        assert complex.n_functions() == 3

    def test_empty(self, empty):
        assert empty.n_functions() == 0


class TestNClasses:
    def test_simple(self, simple):
        assert simple.n_classes() == 0

    def test_complex(self, complex):
        assert complex.n_classes() == 1

    def test_empty(self, empty):
        assert empty.n_classes() == 0


class TestImports:
    def test_simple(self, simple):
        assert simple.n_imports() == 0

    def test_complex(self, complex):
        assert complex.n_imports() == 0

    def test_empty(self, empty):
        assert empty.n_imports() == 0

    def test_imports(self, imports):
        assert imports.n_imports() == 3


class TestNModules:
    def test_simple(self, simple):
        assert simple.n_imported_modules() == 0

    def test_complex(self, complex):
        assert complex.n_imported_modules() == 0

    def test_empty(self, empty):
        assert empty.n_imported_modules() == 0

    def test_imports(self, imports):
        assert imports.n_imported_modules() == 2  # math and operator


class TestCyclomaticComplexity:
    def test_simple(self, simple):
        assert simple.cc(total=True) == 1

    def test_simple_per_function(self, simple):
        assert simple.cc(total=False, use_median=False) == 1
        assert simple.cc(total=False, use_median=True) == 1

    def test_cc(self, cc):
        # Not sure why 10 and not 7.
        # It could be due to Class definition,
        # hidden constructor and module-level complexity.
        assert cc.cc(total=True) == 10

    def test_cc_per_function(self, cc):
        assert cc.cc(total=False, use_median=False) == (1 + 3 + 1 + 2) / 4
        assert cc.cc(total=False, use_median=True) == 1.5

    def test_empty(self, empty):
        assert empty.cc(total=False) == 0
        assert empty.cc(total=True) == 0

    def test_comment_only(self, comment_only):
        assert comment_only.cc(total=False) == 0
        assert comment_only.cc(total=True) == 0


class TestCognitiveComplexity:
    def test_simple(self, simple):
        assert simple.cogc(total=False, use_median=False) == 0
        assert simple.cogc(total=True) == 0

    def test_cogc(self, cogc):
        assert cogc.cogc(total=True) == 6

    def test_cogc_per_function(self, cogc):
        assert cogc.cogc(total=False, use_median=False) == (0 + 6 + 0) / 3
        assert cogc.cogc(total=False, use_median=True) == 0

    def test_empty(self, empty):
        assert empty.cogc(total=False) == 0
        assert empty.cogc(total=True) == 0

    def test_comment_only(self, comment_only):
        assert comment_only.cogc(total=False) == 0
        assert comment_only.cogc(total=True) == 0


class TestHalsteadMetrics:
    def test_simple(self, simple):
        assert simple.halstead(total=False).mean() == 0.0

    def test_halstead(self, halstead):
        metrics = halstead.halstead(total=True)
        assert metrics.mean() > 0.0

        vocabulary = 3 + 3 + 5 + 2  # not sure why 2 for x + y
        assert np.isclose(metrics.loc["vocabulary"], vocabulary)

        length = 3 + 3 + 6 + 3
        assert np.isclose(metrics.loc["length"], length)

    def test_halstead_mean(self, halstead):
        metrics = halstead.halstead(total=False, use_median=False)
        assert metrics.mean() > 0.0

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
        assert metrics.mean() > 0.0

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

    def test_comment_only(self, comment_only):
        assert comment_only.halstead(total=False).mean() == 0.0


class TestUserDefinedNames:
    def test_simple(self, simple):
        assert simple.user_defined_names() == {"hello"}

    def test_user_defined_names(self, user_defined_names):
        names = user_defined_names.user_defined_names()

        expected = {
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
        }
        assert names == expected

    def test_empty(self, empty):
        assert empty.user_defined_names() == set()

    def test_comment_only(self, comment_only):
        assert comment_only.user_defined_names() == set()


class TestComments:
    def test_comment_only(self, comment_only):
        comments = comment_only.comments()
        assert len(comments) == 3
        assert comments[0] == "Just a comment"
        assert comments[1] == "Another comment"
        assert comments[2] == "Third comment"

    def test_complex(self, complex):
        comments = complex.comments()
        assert len(comments) == 4
        assert comments[0] == "Comment line"

    def test_mixed_docstrings(self, mixed_docstrings):
        comments = mixed_docstrings.comments()
        assert len(comments) == 4
        assert comments[0] == "Header comment"
        assert comments[1] == "inline comment"
        assert comments[2] == "Another comment"
        assert comments[3] == "Footer comment"

    def test_unicode_content(self, unicode_content):
        comments = unicode_content.comments()
        assert len(comments) == 1
        assert comments[0] == "Comment with unicode: café"

    def test_multiline_strings(self, multiline_strings):
        comments = multiline_strings.comments()
        assert len(comments) == 0

    def test_whitespace_only(self, whitespace_only):
        comments = whitespace_only.comments()
        assert len(comments) == 0

    def test_empty(self, empty):
        comments = empty.comments()
        assert len(comments) == 0


class TestDocstrings:
    def test_simple(self, simple):
        docstrings = simple.docstrings()
        assert len(docstrings) == 0

    def test_complex(self, complex):
        docstrings = complex.docstrings()
        assert len(docstrings) == 3
        assert "Module docstring" in docstrings[0]
        assert docstrings[1] == "Function docstring."
        assert docstrings[2] == "Class docstring."

    def test_empty(self, empty):
        docstrings = empty.docstrings()
        assert len(docstrings) == 0

    def test_comment_only(self, comment_only):
        docstrings = comment_only.docstrings()
        assert len(docstrings) == 0
