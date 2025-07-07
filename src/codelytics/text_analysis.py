import pandas as pd
import re


class TextAnalysis:
    """
    Base class for analyzing text content.

    Provides common functionality for analyzing collections of text strings
    such as comments and docstrings.

    Parameters
    ----------
    texts : list of str
        List of text strings to analyze.

    """

    def __init__(self, texts):
        self.texts = texts

    def __len__(self):
        """Return the number of text items."""
        return len(self.texts)

    def _stat(self, values, total=False, use_median=False):
        """Calculate statistics from values."""
        if not values:
            return 0

        if total:
            return sum(values)
        elif use_median:
            return float(pd.Series(values).median())
        else:
            return float(pd.Series(values).mean())

    def n_words(self, total=False, use_median=False):
        """
        Return word count statistics.

        Parameters
        ----------
        total : bool, optional
            If True, returns total number of words across all texts.
            If False, returns mean or median words per text (default).
        use_median : bool, optional
            If True and total=False, returns median words per text.
            If False and total=False, returns mean words per text.
            Ignored when total=True.

        Returns
        -------
        int or float
            Total, mean, or median word count.
        """
        word_counts = [len(text.split()) for text in self.texts]
        return self._stat(word_counts, total, use_median)

    def n_chars(self, total=False, use_median=False):
        """
        Return character count statistics.

        Parameters
        ----------
        total : bool, optional
            If True, returns total number of characters across all texts.
            If False, returns mean or median characters per text (default).
        use_median : bool, optional
            If True and total=False, returns median characters per text.
            If False and total=False, returns mean characters per text.
            Ignored when total=True.

        Returns
        -------
        int or float
            Total, mean, or median character count.
        """
        char_counts = [len(text) for text in self.texts]
        return self._stat(char_counts, total, use_median)

    def n_non_ascii(self, total=False, use_median=False):
        """
        Return non-ASCII character count statistics.

        Parameters
        ----------
        total : bool, optional
            If True, returns total number of non-ASCII characters across all texts.
            If False, returns mean or median non-ASCII characters per text (default).
        use_median : bool, optional
            If True and total=False, returns median non-ASCII characters per text.
            If False and total=False, returns mean non-ASCII characters per text.
            Ignored when total=True.

        Returns
        -------
        int or float
            Total, mean, or median non-ASCII character count.
        """
        non_ascii_counts = []
        for text in self.texts:
            count = len([char for char in text if ord(char) > 127])
            non_ascii_counts.append(count)
        return self._stat(non_ascii_counts, total, use_median)

    def n_sentences(self, total=False, use_median=False):
        """
        Return sentence count statistics.

        Counts complete sentences that begin with an uppercase letter
        and end with sentence-ending punctuation (., !, ?).

        Parameters
        ----------
        total : bool, optional
            If True, returns total number of sentences across all texts.
            If False, returns mean or median sentences per text (default).
        use_median : bool, optional
            If True and total=False, returns median sentences per text.
            If False and total=False, returns mean sentences per text.
            Ignored when total=True.

        Returns
        -------
        int or float
            Total, mean, or median sentence count.
        """
        sentence_counts = []
        sentence_pattern = re.compile(r"[A-Z][^.!?]*[.!?]")

        for text in self.texts:
            sentences = sentence_pattern.findall(text)
            sentence_counts.append(len(sentences))

        return self._stat(sentence_counts, total, use_median)
