import pathlib
import tempfile

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
def inline_comments():
    code = """x = 1  # This is an inline comment
y = 2  # Another inline comment
"""
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
        assert simple.loc() == 4

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

    def test_inline_comments_counted_as_source(self, inline_comments):
        assert inline_comments.loc() == 2
        assert inline_comments.lloc() == 2
        assert inline_comments.sloc() == 2

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
