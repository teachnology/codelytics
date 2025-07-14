import numpy as np
import pandas as pd

# All statistics keys available in Dir.stats()
STATS_KEYS = [
    # Repository metrics
    "is_repo",
    "n_commits",
    # File counts
    "n_files_total",
    "n_files_py",
    "n_files_ipynb",
    "n_files_md",
    # Radon metrics
    "radon_loc",
    "radon_lloc",
    "radon_sloc",
    "radon_comments",
    "radon_multi",
    "radon_blank",
    # Custom LLOC
    "lloc",
    # Basic code metrics
    "n_char",
    "n_functions",
    "n_classes",
    "n_imports",
    "n_imported_modules",
    # McCabe complexity
    "mccabe_total",
    "mccabe_mean",
    "mccabe_median",
    # Cognitive complexity
    "cognitive_total",
    "cognitive_mean",
    "cognitive_median",
    # Halstead metrics
    "halstead_vocabulary_total",
    "halstead_vocabulary_mean",
    "halstead_vocabulary_median",
    "halstead_length_total",
    "halstead_length_mean",
    "halstead_length_median",
    "halstead_volume_total",
    "halstead_volume_mean",
    "halstead_volume_median",
    "halstead_difficulty_total",
    "halstead_difficulty_mean",
    "halstead_difficulty_median",
    "halstead_effort_total",
    "halstead_effort_mean",
    "halstead_effort_median",
    # Comment analysis
    "comments_count",
    "comments_words_total",
    "comments_words_mean",
    "comments_words_median",
    "comments_chars_total",
    "comments_chars_mean",
    "comments_chars_median",
    "comments_non_ascii_total",
    "comments_non_ascii_mean",
    "comments_non_ascii_median",
    "comments_sentences_total",
    "comments_sentences_mean",
    "comments_sentences_median",
    "comments_misspelled_total",
    "comments_misspelled_mean",
    "comments_misspelled_median",
    "comments_why_or_what_total",
    "comments_why_or_what_mean",
    "comments_why_or_what_median",
    # Docstring analysis
    "docstrings_count",
    "docstrings_words_total",
    "docstrings_words_mean",
    "docstrings_words_median",
    "docstrings_chars_total",
    "docstrings_chars_mean",
    "docstrings_chars_median",
    "docstrings_non_ascii_total",
    "docstrings_non_ascii_mean",
    "docstrings_non_ascii_median",
    "docstrings_sentences_total",
    "docstrings_sentences_mean",
    "docstrings_sentences_median",
    "docstrings_misspelled_total",
    "docstrings_misspelled_mean",
    "docstrings_misspelled_median",
    # Name analysis
    "names_count",
    "names_chars_total",
    "names_chars_mean",
    "names_chars_median",
    "names_camel_case_ratio",
    "names_snake_case_ratio",
    "names_pascal_case_ratio",
    "names_private_ratio",
    "names_endswith_number_ratio",
    "names_simple_ratio",
    "names_ascii_ratio",
    # Notebook metrics
    "n_cells_total",
    "n_cells_code",
    "n_cells_markdown",
    # Markdown analysis
    "markdown_words_total",
    "markdown_chars_total",
    "markdown_sentences_total",
    "markdown_non_ascii_total",
    "markdown_misspelled_total",
]


def stats_nan(dir_name):
    """
    Create a Series with NaN values for all statistics keys.

    Parameters
    ----------
    dir_name : str
        Name of the directory.

    Returns
    -------
    pd.Series
        Series with name as index and NaN values.
    """
    return pd.Series({key: np.nan for key in STATS_KEYS}, name=dir_name)
