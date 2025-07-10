import re

import pandas as pd
from spellchecker import SpellChecker


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

    def __getitem__(self, index):
        """Return text at the specified index."""
        return self.texts[index]

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

    def misspelled_words(self, total=False, use_median=False):
        """
        Return misspelled word count statistics.

        Counts misspelled words in all texts using the pyspellchecker library.
        Only counts actual words (excludes code-like tokens, URLs, etc.).

        Parameters
        ----------
        total : bool, optional
            If True, returns total number of misspelled words across all texts.
            If False, returns mean or median misspelled words per text (default).
        use_median : bool, optional
            If True and total=False, returns median misspelled words per text.
            If False and total=False, returns mean misspelled words per text.
            Ignored when total=True.

        Returns
        -------
        int or float
            Total, mean, or median misspelled word count.
            Returns 0 or 0.0 if spellchecker is not available.
        """
        try:
            spell = SpellChecker()
            misspelled_counts = []

            for text in self.texts:
                # Split into words and clean them
                words = text.split()
                cleaned_words = []

                for word in words:
                    # Remove punctuation and convert to lowercase
                    cleaned_word = re.sub(r"[^\w]", "", word.lower())

                    # Only include words that are likely actual words.
                    if (
                        cleaned_word
                        and cleaned_word.isalpha()
                        and len(cleaned_word) > 1
                        and not cleaned_word.isupper()
                    ):  # Skip ALL_CAPS (likely constants)
                        cleaned_words.append(cleaned_word)

                # Find misspelled words
                misspelled = spell.unknown(cleaned_words)
                misspelled_counts.append(len(misspelled))

            return self._stat(misspelled_counts, total, use_median)

        except ImportError:
            # Fallback if pyspellchecker is not available
            return 0

    def why_or_what(self, total=False, use_median=False):
        """
        Return count of texts that explain 'why' versus 'what'.

        Analyzes texts to determine if they explain the rationale/reason (why)
        or describe what the code is doing (what). Useful for evaluating
        comment quality - good comments explain why, not what.

        Parameters
        ----------
        total : bool, optional
            If True, returns total number of 'why' texts across all texts.
            If False, returns mean or median 'why' texts per text (default).
        use_median : bool, optional
            If True and total=False, returns median 'why' texts per text.
            If False and total=False, returns mean 'why' texts per text.
            Ignored when total=True.

        Returns
        -------
        int or float
            Total, mean, or median count of texts that explain 'why'.
            Returns 0 or 0.0 if no texts found.
        """
        why_counts = []

        for text in self.texts:
            if not text.strip():
                why_counts.append(0)
                continue

            text_lower = text.lower()
            why_score = 0
            what_score = 0

            # Strong 'why' indicators (higher weight)
            strong_why_patterns = [
                r"\b(because|since|due to|reason|rationale)\b",
                r"\b(to avoid|to prevent|to ensure|to guarantee)\b",
                r"\b(performance|optimization|efficiency|speed)\b",
                r"\b(security|safety|protection|vulnerability)\b",
                r"\b(compatibility|support|legacy|backwards)\b",
                r"\b(hack|workaround|fixme|todo)\b",
                r"\b(important|warning|note|careful|attention)\b",
                r"\b(design decision|trade-?off|compromise)\b",
                r"\b(expensive|slow|fast|improve|better)\b",
            ]

            for pattern in strong_why_patterns:
                matches = len(re.findall(pattern, text_lower))
                why_score += matches * 3  # Higher weight for strong indicators

            # Moderate 'why' indicators
            moderate_why_patterns = [
                r"\b(bug|issue|problem|fix)\b",
                r"\b(requirement|needed|necessary)\b",
                r"\b(limitation|constraint|restriction)\b",
                r"\b(assumption|expect|assume)\b",
                r"\b(why|purpose|motivation)\b",
            ]

            for pattern in moderate_why_patterns:
                matches = len(re.findall(pattern, text_lower))
                why_score += matches * 2

            # Strong 'what' indicators (only descriptive actions without rationale)
            strong_what_patterns = [
                r"^(initialize|setup|configure|prepare)\b",
                r"^(get|set|create|delete|update|modify)\b",
                r"^(call|invoke|execute|run|process)\b",
                r"^(return|output|result|value)\b",
                r"^(loop|iterate|through|over)\b",
                r"^(calculate|compute|determine|find)\b",
                r"^(parse|format|convert|transform)\b",
                r"^(store|save|load|read|write)\b",
                r"^(sort|filter|search|match)\b",
                r"^(print|display|show|log)\b",
                r"\b(this function|this method|here we)\b",
            ]

            for pattern in strong_what_patterns:
                matches = len(re.findall(pattern, text_lower))
                what_score += matches * 2

            # Step-by-step indicators (strong 'what')
            if any(
                phrase in text_lower
                for phrase in ["first,", "then,", "next,", "finally,", "step "]
            ):
                what_score += 2

            # Additional context clues
            if any(
                phrase in text_lower
                for phrase in [
                    "attack",
                    "injection",
                    "version",
                    "old",
                    "new",
                    "time",
                    "memory",
                ]
            ):
                why_score += 1

            # Determine if this text explains 'why' (1) or 'what' (0)
            explains_why = 1 if why_score > what_score else 0
            why_counts.append(explains_why)

        return self._stat(why_counts, total, use_median)
