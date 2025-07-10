import numpy as np
import pytest

import codelytics as cdl


@pytest.fixture
def simple():
    return cdl.TextAnalysis(["Hello world.", "This is a test.", "Short."])


@pytest.fixture
def empty():
    return cdl.TextAnalysis([])


@pytest.fixture
def unicode():
    return cdl.TextAnalysis(
        [
            "This is a sentence. Another sentence here.",
            "Unicode test: café résumé naïve.",
            "Multiple words with numbers 123 and symbols!",
        ]
    )


@pytest.fixture
def sentences():
    return cdl.TextAnalysis(
        [
            "This is a sentence. Another",
            "add value",
            "Multiple words with numbers 123 and symbols!",
            "Messy text with inconsistent spacing and punctuation...",
        ]
    )


@pytest.fixture
def spell_check():
    return cdl.TextAnalysis(
        [
            "This is a simple test.",
            "Ths is a smple tst with some misspelled words.",
            "Another sentence with no errors.",
        ]
    )


@pytest.fixture
def why_or_what():
    return cdl.TextAnalysis(
        [
            # 'Why' comments (explaining rationale/reasoning)
            "Use binary search because linear search is too slow for large datasets",
            "Cache results to avoid expensive database queries",
            "TODO: Refactor this code due to performance issues",
            "Hack: Using comparison since datetime parsing fails on old versions",
            "Important: Always validate input to prevent SQL injection attacks",
            "We need this workaround for IE compatibility",
            "This optimization improves response time by 50%",
            "Disable logging in production for security reasons",
            "Keep this for backwards compatibility with v1.0",
            "Design decision: Using composition over inheritance here",
            # 'What' comments (describing actions/implementation)
            "Initialize the counter to zero",
            "Loop through all items in the list",
            "Get the current user from session",
            "This function calculates the total price",
            "First, validate the input parameters",
            "Then, process each record in the database",
            "Finally, return the formatted result",
            "Here we create a new instance of the class",
            "Sort the array in ascending order",
            "Parse the JSON response from the API",
            "Print debug information to console",
            "Set the default configuration values",
            "",  # Empty comment
        ]
    )


class TestInit:
    def test_simple(self, simple):
        assert len(simple) == 3
        assert simple[2] == "Short."

    def test_empty(self, empty):
        assert len(empty) == 0


class TestNWords:
    def test_total(self, simple):
        assert simple.n_words(total=True) == 7

    def test_mean(self, simple):
        assert simple.n_words(total=False, use_median=False) == (2 + 4 + 1) / 3

    def test_median(self, simple):
        assert simple.n_words(total=False, use_median=True) == 2.0

    def test_empty(self, empty):
        assert empty.n_words() == 0.0
        assert empty.n_words(total=True) == 0


class TestNChars:
    def test_total(self, simple):
        assert simple.n_chars(total=True) == 33

    def test_mean(self, simple):
        assert simple.n_chars(total=False, use_median=False) == (12 + 15 + 6) / 3

    def test_median(self, simple):
        assert simple.n_chars(total=False, use_median=True) == 12.0

    def test_empty(self, empty):
        assert empty.n_chars() == 0.0
        assert empty.n_chars(total=True) == 0


class TestNNonAscii:
    def test_simple(self, simple):
        assert simple.n_non_ascii(total=True) == 0
        assert simple.n_non_ascii(total=False, use_median=False) == 0.0
        assert simple.n_non_ascii(total=False, use_median=True) == 0.0

    def test_unicode(self, unicode):
        assert unicode.n_non_ascii(total=True) == 4  # café (1) + résumé (2) + naïve (1)
        assert np.isclose(
            unicode.n_non_ascii(total=False, use_median=False), (0 + 4 + 0) / 3
        )
        assert unicode.n_non_ascii(total=False, use_median=True) == 0

    def test_empty(self, empty):
        assert empty.n_non_ascii() == 0.0
        assert empty.n_non_ascii(total=True) == 0


class TestNSentences:
    def test_simple(self, simple):
        assert simple.n_sentences(total=True) == 3
        assert simple.n_sentences(total=False, use_median=False) == 1.0
        assert simple.n_sentences(total=False, use_median=True) == 1.0

    def test_sentences(self, sentences):
        assert sentences.n_sentences(total=True) == 3
        assert np.isclose(
            sentences.n_sentences(total=False, use_median=False), (1 + 0 + 1 + 1) / 4
        )
        assert sentences.n_sentences(total=False, use_median=True) == 1.0

    def test_empty(self, empty):
        assert empty.n_sentences() == 0.0
        assert empty.n_sentences(total=True) == 0


class TestSpellCheck:
    def test_spell_check(self, spell_check):
        assert spell_check.misspelled_words(total=True) == 3
        assert np.isclose(
            spell_check.misspelled_words(total=False, use_median=False), (0 + 3 + 0) / 3
        )
        assert np.isclose(spell_check.misspelled_words(total=False, use_median=True), 0)

    def test_empty(self, empty):
        assert empty.misspelled_words() == 0.0
        assert empty.misspelled_words(total=True) == 0

    def test_no_errors(self, simple):
        assert simple.misspelled_words() == 0.0
        assert simple.misspelled_words(total=True) == 0


class TestWhyOrWhat:
    def test_total(self, why_or_what):
        # Should count approximately 10-11 'why' comments out of 26 total
        assert 8 <= why_or_what.why_or_what(total=True) <= 12

    def test_mean(self, why_or_what):
        result = why_or_what.why_or_what()
        # Should be around 0.4-0.5 (proportion of 'why' comments)
        assert 0.4 <= result <= 0.6
