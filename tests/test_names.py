import pytest
import pandas as pd
from codelytics import Names


@pytest.fixture
def simple():
    return Names({"var", "function_name", "ClassName", "x", "very_long_variable_name"})


@pytest.fixture
def empty():
    return Names(set())


@pytest.fixture
def single():
    return Names({"single"})


@pytest.fixture
def cases():
    return Names(
        {"camelCase", "snake_case", "PascalCase", "_private", "simple", "var23"}
    )


@pytest.fixture
def ascii():
    return Names({"ascii_name", "name_with_emoji_😀", "名字_with_chinese"})


class TestInit:
    def test_init(self, simple):
        expected = {"var", "function_name", "ClassName", "x", "very_long_variable_name"}
        assert simple.names == expected

    def test_init_empty(self, empty):
        assert empty.names == set()


class TestLen:
    def test_len(self, simple):
        assert len(simple) == 5

    def test_len_empty(self, empty):
        assert len(empty) == 0

    def test_len_single(self, single):
        assert len(single) == 1


class TestNChars:
    def test_n_chars(self, simple):
        result = simple.n_chars()

        assert result.loc["var"] == 3
        assert result.loc["function_name"] == 13
        assert result.loc["ClassName"] == 9
        assert result.loc["x"] == 1
        assert result.loc["very_long_variable_name"] == 23

    def test_n_chars_empty(self, empty):
        assert len(empty.n_chars()) == 0

    def test_n_chars_single_name(self, single):
        assert single.n_chars().loc["single"] == 6


class TestCases:
    def test_camel_case(self, cases):
        result = cases.camel_case()
        expected = pd.Series(
            {
                "camelCase": True,
                "snake_case": False,
                "PascalCase": False,
                "_private": False,
                "simple": True,
                "var23": False,
            },
            name="camel_case",
        )
        assert result.sort_index().equals(expected.sort_index())

    def test_snake_case(self, cases):
        result = cases.snake_case()
        expected = pd.Series(
            {
                "camelCase": False,
                "snake_case": True,
                "PascalCase": False,
                "_private": False,
                "simple": True,
                "var23": False,
            },
            name="snake_case",
        )
        assert result.sort_index().equals(expected.sort_index())

    def test_pascal_case(self, cases):
        result = cases.pascal_case()
        expected = pd.Series(
            {
                "camelCase": False,
                "snake_case": False,
                "PascalCase": True,
                "_private": False,
                "simple": False,
                "var23": False,
            },
            name="pascal_case",
        )
        assert result.sort_index().equals(expected.sort_index())

    def test_private(self, cases):
        result = cases.private()
        expected = pd.Series(
            {
                "camelCase": False,
                "snake_case": False,
                "PascalCase": False,
                "_private": True,
                "simple": False,
                "var23": False,
            },
            name="private",
        )
        assert result.sort_index().equals(expected.sort_index())

    def test_endswith_number(self, cases):
        result = cases.endswith_number()
        expected = pd.Series(
            {
                "camelCase": False,
                "snake_case": False,
                "PascalCase": False,
                "_private": False,
                "simple": False,
                "var23": True,
            },
            name="endswith_number",
        )
        assert result.sort_index().equals(expected.sort_index())


class TestAscii:
    def test_ascii(self, ascii):
        result = ascii.ascii()
        expected = pd.Series(
            {
                "ascii_name": True,
                "name_with_emoji_😀": False,
                "名字_with_chinese": False,
            },
            name="ascii",
        )
        assert result.sort_index().equals(expected.sort_index())

    def test_ascii_cases(self, cases):
        assert cases.ascii().all()  # All names in cases are ASCII


class TestStats:
    def test_stats(self, simple):
        result = simple.stats()
        expected_columns = [
            "n_chars",
            "camel_case",
            "snake_case",
            "pascal_case",
            "private",
            "endswith_number",
            "ascii",
        ]
        assert result.shape == (5, len(expected_columns))
        assert result.columns.tolist() == expected_columns

        assert result.loc["var", "n_chars"] == 3
        assert not result.loc["function_name", "camel_case"]
        assert result.loc["ClassName", "pascal_case"]
