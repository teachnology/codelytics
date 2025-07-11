import pytest

import codelytics as cdl


@pytest.fixture
def empty():
    return cdl.Names(names=[])


@pytest.fixture
def names():
    return cdl.Names(
        names=[
            "camelCase",
            "snake_case",
            "PascalCase",
            "_private",
            "simple",
            "var23",
            "x",
            "very_long_variable_name",
        ]
    )


@pytest.fixture
def ascii():
    return cdl.Names(names=["ascii_name", "name_with_emoji_😀", "名字_with_chinese"])


class TestInit:
    def test_names(self, names):
        assert len(names) == 8
        assert "x" in names.names

    def test_empty(self, empty):
        assert empty.names == []
        assert len(empty) == 0


class TestNChars:
    def test_n_chars(self, names):
        result = names.n_chars

        assert result.loc["camelCase"] == 9
        assert result.loc["snake_case"] == 10
        assert result.loc["PascalCase"] == 10
        assert result.loc["_private"] == 8
        assert result.loc["simple"] == 6
        assert result.loc["var23"] == 5
        assert result.loc["x"] == 1
        assert result.loc["very_long_variable_name"] == 23

    def test_n_chars_empty(self, empty):
        assert empty.n_chars.size == 0


class TestCases:
    def test_camel_case(self, names):
        assert names.camel_case.loc["camelCase"]
        assert not names.camel_case.loc["PascalCase"]
        assert names.camel_case.loc["x"]
        assert names.camel_case.sum() == 3

    def test_snake_case(self, names):
        assert names.snake_case.loc["snake_case"]
        assert not names.snake_case.loc["PascalCase"]
        assert names.snake_case.sum() == 4

    def test_pascal_case(self, names):
        assert names.pascal_case.loc["PascalCase"]
        assert names.pascal_case.sum() == 1

    def test_private(self, names):
        assert names.private.loc["_private"]
        assert names.private.sum() == 1

    def test_endswith_number(self, names):
        assert names.endswith_number.loc["var23"]
        assert names.endswith_number.sum() == 1

    def test_simple(self, names):
        assert names.simple.loc["simple"]
        assert names.simple.loc["x"]
        assert not names.simple.loc["very_long_variable_name"]
        assert not names.simple.loc["var23"]
        assert names.simple.sum() == 2


class TestAscii:
    def test_ascii_cases(self, names):
        assert names.ascii.all()  # All names in cases are ASCII

    def test_ascii(self, ascii):
        assert ascii.ascii.sum() == 1
        assert ascii.ascii.loc["ascii_name"]


class TestStats:
    def test_stats(self, names):
        result = names.stats
        expected_columns = [
            "n_chars",
            "camel_case",
            "snake_case",
            "pascal_case",
            "private",
            "endswith_number",
            "simple",
            "ascii",
        ]
        assert result.shape == (8, len(expected_columns))
        assert result.columns.tolist() == expected_columns

        assert result.loc["var23", "n_chars"] == 5
        assert not result.loc["snake_case", "camel_case"]
        assert result.loc["PascalCase", "pascal_case"]
