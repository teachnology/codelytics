import pathlib
import subprocess

import numpy as np
import pandas as pd

from .notebook import Notebook
from .py import Py
from .text_analysis import TextAnalysis


class Dir:
    """
    Analyse directory structure and git repository information.

    This class provides methods to analyse directories, check if they are git
    repositories, count commits, iterate through files, and count files by type.

    Parameters
    ----------
    path : str or pathlib.Path
        Path to the directory to analyse

    Raises
    ------
    FileNotFoundError
        If the specified directory does not exist
    NotADirectoryError
        If the specified path is not a directory
    """

    def __init__(self, path):
        self.path = pathlib.Path(path)

        if not self.path.exists():
            raise FileNotFoundError(f"Directory does not exist: {self.path}")

        if not self.path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {self.path}")

    @property
    def is_repo(self):
        """
        Check if the directory is a git repository.

        Returns
        -------
        bool
            True if directory is a git repository, False otherwise
        """
        git_dir = self.path / ".git"
        return git_dir.exists() and git_dir.is_dir()

    def n_commits(self, ref="HEAD"):
        """
        Get the number of commits in the git repository.

        Parameters
        ----------
        ref : str, default 'HEAD'
            Git reference to count commits from. Can be 'HEAD' for current
            branch, '--all' for all branches, or any specific branch name.

        Returns
        -------
        int
            Number of commits in the repository

        Raises
        ------
        RuntimeError
            If the directory is not a git repository or git command fails
        """
        if not self.is_repo:
            raise RuntimeError("Directory is not a git repository")

        try:
            result = subprocess.run(
                ["git", "rev-list", "--count", ref],
                cwd=self.path,
                capture_output=True,
                text=True,
                check=True,
            )
            return int(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get commit count: {e}")
        except FileNotFoundError:
            raise RuntimeError("Git command not found.")

    def __iter__(self):
        """
        Iterate recursively through all files in the directory.

        Yields
        ------
        pathlib.Path
            Path object for each file found recursively
        """
        for file_path in self.path.rglob("*"):
            if file_path.is_file():
                yield file_path

    def __len__(self):
        """
        Get the total number of files in the directory.

        Returns
        -------
        int
            Total number of files found recursively in the directory
        """
        return sum(1 for _ in self)

    def iter_files(self, suffix=None):
        """
        Iterate recursively through files with optional suffix filter.

        Parameters
        ----------
        suffix : str, optional
            File extension to filter by (with or without the dot). If None, behaves the
            same as __iter__ and yields all files.

        Yields
        ------
        pathlib.Path
            Path object for each file found recursively, optionally filtered by suffix
        """
        if suffix is None:
            yield from self
        else:
            if not suffix.startswith("."):
                suffix = "." + suffix

            for file_path in self:
                if file_path.suffix == suffix:
                    yield file_path

    def n_files(self, suffix=None):
        """
        Count the number of files in the directory.

        Parameters
        ----------
        suffix : str, optional
            File extension to filter by (with or without the dot).
            If None, counts all files.

        Returns
        -------
        int
            Number of files matching the criteria
        """
        return sum(1 for _ in self.iter_files(suffix=suffix))

    def extract(self, content_type):
        """
        Extract and merge content from all files in the directory.

        Extracts content from Python files, Jupyter notebooks, and Markdown files
        based on the specified content type. For code content, filters out files
        and cells with invalid Python syntax.

        Parameters
        ----------
        content_type : str
            Type of content to extract. Options are:
            - 'code': Extract code from .py files and code cells from .ipynb files
                    (excludes files/cells with syntax errors)
            - 'markdown': Extract from .md files and markdown cells from .ipynb files

        Returns
        -------
        Py or TextAnalysis object
            Each file's content is separated by double newlines.
            For code content, only includes syntactically valid Python code.
            Returns empty content if no valid files found or content type not
            recognized.
        """
        if content_type not in ["code", "markdown"]:
            raise ValueError("Invalid content_type. Use 'code' or 'markdown'.")

        content_parts = []

        for file_path in self:
            try:
                content = None

                if content_type == "code":
                    if file_path.suffix == ".py":
                        try:
                            temp_py = Py(file_path)
                            if temp_py.is_valid_syntax:
                                content = temp_py.content
                        except Exception:
                            # Skip files that can't be processed
                            continue

                    elif file_path.suffix == ".ipynb":
                        nb = Notebook(file_path)
                        # Notebook.extract("code") already filters out invalid syntax.
                        extracted_code = nb.extract("code")
                        if (
                            extracted_code.content.strip()
                        ):  # Only add if there's valid content
                            content = extracted_code.content

                elif content_type == "markdown":
                    if file_path.suffix == ".md":
                        content = file_path.read_text(encoding="utf-8")

                    elif file_path.suffix == ".ipynb":
                        nb = Notebook(file_path)
                        content = nb.extract("markdown")[0]

                # Only add content if it exists and is not empty
                if content and content.strip():
                    content_parts.append(content)

            except Exception:
                # Skip files that cause any processing errors
                continue

        source = "\n\n".join(content_parts)
        return Py(source) if content_type == "code" else TextAnalysis([source])

    def stats(self):
        """
        Extract comprehensive statistics from all files in the directory.

        Analyzes all Python files, Jupyter notebooks, and Markdown files to extract
        code metrics, text analysis, and repository statistics. Returns a pandas
        Series with the directory name as index and various statistics as values.

        Returns
        -------
        pd.Series
            Series with directory name as index and comprehensive statistics including:

            Repository metrics:
            - is_repo: Whether directory is a git repository
            - n_commits: Number of commits (if git repo)

            File counts:
            - n_files_total: Total number of files
            - n_files_py: Number of Python files
            - n_files_ipynb: Number of Jupyter notebook files
            - n_files_md: Number of Markdown files

            Code metrics (from all valid Python code):
            - loc: Physical lines of code
            - lloc: Logical lines of code (excluding docstrings)
            - sloc: Source lines of code
            - comments: Number of comment lines
            - multi: Number of multi-line comments
            - blank: Number of blank lines
            - n_char: Total characters
            - n_functions: Number of function definitions
            - n_classes: Number of class definitions
            - n_imports: Number of import statements
            - n_imported_modules: Number of unique imported modules
            - cc_total: Total cyclomatic complexity
            - cc_mean: Mean cyclomatic complexity per function
            - cc_median: Median cyclomatic complexity per function
            - mccabe_total: Total McCabe complexity
            - mccabe_mean: Mean McCabe complexity per function
            - mccabe_median: Median McCabe complexity per function
            - cognitive_total: Total cognitive complexity
            - cognitive_mean: Mean cognitive complexity per function
            - cognitive_median: Median cognitive complexity per function
            - halstead_*: Halstead (vocabulary, length, volume, difficulty, effort)

            Text analysis (comments and docstrings):
            - comments_*: Comment analysis metrics
            - docstrings_*: Docstring analysis metrics

            Naming analysis:
            - names_*: User-defined name statistics

            Notebook metrics:
            - n_cells_total: Total cells in all notebooks
            - n_cells_code: Total code cells
            - n_cells_markdown: Total markdown cells
        """
        # Initialize statistics dictionary
        stats_dict = {}

        # Directory name (not full path)
        dir_name = self.path.name

        # Repository metrics
        stats_dict["is_repo"] = self.is_repo
        if self.is_repo:
            try:
                stats_dict["n_commits"] = self.n_commits(ref="HEAD")
            except Exception:
                stats_dict["n_commits"] = np.nan
        else:
            stats_dict["n_commits"] = 0

        # File counts
        stats_dict["n_files_total"] = len(self)
        stats_dict["n_files_py"] = self.n_files("py")
        stats_dict["n_files_ipynb"] = self.n_files("ipynb")
        stats_dict["n_files_md"] = self.n_files("md")

        # Extract and analyze all code
        all_code = self.extract("code")

        # Radon metrics
        if all_code.radon_analysis is not None:
            radon = all_code.radon_analysis
            stats_dict["radon_loc"] = radon.loc
            stats_dict["radon_lloc"] = radon.lloc
            stats_dict["radon_sloc"] = radon.sloc
            stats_dict["radon_comments"] = radon.comments
            stats_dict["radon_multi"] = radon.multi
            stats_dict["radon_blank"] = radon.blank
        else:
            stats_dict["radon_loc"] = np.nan
            stats_dict["radon_lloc"] = np.nan
            stats_dict["radon_sloc"] = np.nan
            stats_dict["radon_comments"] = np.nan
            stats_dict["radon_multi"] = np.nan
            stats_dict["radon_blank"] = np.nan

        # LLOC (custom calculation excluding docstrings)
        stats_dict["lloc"] = all_code.lloc

        # Basic code metrics
        stats_dict["n_char"] = all_code.n_char
        stats_dict["n_functions"] = all_code.n_functions
        stats_dict["n_classes"] = all_code.n_classes
        stats_dict["n_imports"] = all_code.n_imports
        stats_dict["n_imported_modules"] = all_code.n_imported_modules

        # McCabe complexity
        stats_dict["mccabe_total"] = all_code.mccabe(total=True)
        stats_dict["mccabe_mean"] = all_code.mccabe(total=False, use_median=False)
        stats_dict["mccabe_median"] = all_code.mccabe(total=False, use_median=True)

        # Cognitive complexity
        stats_dict["cognitive_total"] = all_code.cognitive_complexity(total=True)
        stats_dict["cognitive_mean"] = all_code.cognitive_complexity(
            total=False, use_median=False
        )
        stats_dict["cognitive_median"] = all_code.cognitive_complexity(
            total=False, use_median=True
        )

        # Halstead metrics
        halstead_total = all_code.halstead(total=True)
        halstead_mean = all_code.halstead(total=False, use_median=False)
        halstead_median = all_code.halstead(total=False, use_median=True)

        for metric in ["vocabulary", "length", "volume", "difficulty", "effort"]:
            stats_dict[f"halstead_{metric}_total"] = halstead_total[metric]
            stats_dict[f"halstead_{metric}_mean"] = halstead_mean[metric]
            stats_dict[f"halstead_{metric}_median"] = halstead_median[metric]

        # Text analysis - Comments
        comments = all_code.comments
        if len(comments) > 0:
            stats_dict["comments_count"] = len(comments)
            stats_dict["comments_words_total"] = comments.n_words(total=True)
            stats_dict["comments_words_mean"] = comments.n_words(
                total=False, use_median=False
            )
            stats_dict["comments_words_median"] = comments.n_words(
                total=False, use_median=True
            )
            stats_dict["comments_chars_total"] = comments.n_chars(total=True)
            stats_dict["comments_chars_mean"] = comments.n_chars(
                total=False, use_median=False
            )
            stats_dict["comments_chars_median"] = comments.n_chars(
                total=False, use_median=True
            )
            stats_dict["comments_non_ascii_total"] = comments.n_non_ascii(total=True)
            stats_dict["comments_non_ascii_mean"] = comments.n_non_ascii(
                total=False, use_median=False
            )
            stats_dict["comments_non_ascii_median"] = comments.n_non_ascii(
                total=False, use_median=True
            )
            stats_dict["comments_sentences_total"] = comments.n_sentences(total=True)
            stats_dict["comments_sentences_mean"] = comments.n_sentences(
                total=False, use_median=False
            )
            stats_dict["comments_sentences_median"] = comments.n_sentences(
                total=False, use_median=True
            )
            stats_dict["comments_misspelled_total"] = comments.misspelled_words(
                total=True
            )
            stats_dict["comments_misspelled_mean"] = comments.misspelled_words(
                total=False, use_median=False
            )
            stats_dict["comments_misspelled_median"] = comments.misspelled_words(
                total=False, use_median=True
            )
            stats_dict["comments_why_or_what_total"] = comments.why_or_what(total=True)
            stats_dict["comments_why_or_what_mean"] = comments.why_or_what(
                total=False, use_median=False
            )
            stats_dict["comments_why_or_what_median"] = comments.why_or_what(
                total=False, use_median=True
            )
        else:
            for key in [
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
            ]:
                stats_dict[key] = 0

        # Text analysis - Docstrings
        docstrings = all_code.docstrings
        if len(docstrings) > 0:
            stats_dict["docstrings_count"] = len(docstrings)
            stats_dict["docstrings_words_total"] = docstrings.n_words(total=True)
            stats_dict["docstrings_words_mean"] = docstrings.n_words(
                total=False, use_median=False
            )
            stats_dict["docstrings_words_median"] = docstrings.n_words(
                total=False, use_median=True
            )
            stats_dict["docstrings_chars_total"] = docstrings.n_chars(total=True)
            stats_dict["docstrings_chars_mean"] = docstrings.n_chars(
                total=False, use_median=False
            )
            stats_dict["docstrings_chars_median"] = docstrings.n_chars(
                total=False, use_median=True
            )
            stats_dict["docstrings_non_ascii_total"] = docstrings.n_non_ascii(
                total=True
            )
            stats_dict["docstrings_non_ascii_mean"] = docstrings.n_non_ascii(
                total=False, use_median=False
            )
            stats_dict["docstrings_non_ascii_median"] = docstrings.n_non_ascii(
                total=False, use_median=True
            )
            stats_dict["docstrings_sentences_total"] = docstrings.n_sentences(
                total=True
            )
            stats_dict["docstrings_sentences_mean"] = docstrings.n_sentences(
                total=False, use_median=False
            )
            stats_dict["docstrings_sentences_median"] = docstrings.n_sentences(
                total=False, use_median=True
            )
            stats_dict["docstrings_misspelled_total"] = docstrings.misspelled_words(
                total=True
            )
            stats_dict["docstrings_misspelled_mean"] = docstrings.misspelled_words(
                total=False, use_median=False
            )
            stats_dict["docstrings_misspelled_median"] = docstrings.misspelled_words(
                total=False, use_median=True
            )
        else:
            for key in [
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
            ]:
                stats_dict[key] = 0

        # User-defined names analysis
        names = all_code.user_defined_names
        if len(names) > 0:
            name_stats = names.stats
            stats_dict["names_count"] = len(names)
            stats_dict["names_chars_total"] = name_stats["n_chars"].sum()
            stats_dict["names_chars_mean"] = name_stats["n_chars"].mean()
            stats_dict["names_chars_median"] = name_stats["n_chars"].median()
            stats_dict["names_camel_case_ratio"] = name_stats["camel_case"].mean()
            stats_dict["names_snake_case_ratio"] = name_stats["snake_case"].mean()
            stats_dict["names_pascal_case_ratio"] = name_stats["pascal_case"].mean()
            stats_dict["names_private_ratio"] = name_stats["private"].mean()
            stats_dict["names_endswith_number_ratio"] = name_stats[
                "endswith_number"
            ].mean()
            stats_dict["names_simple_ratio"] = name_stats["simple"].mean()
            stats_dict["names_ascii_ratio"] = name_stats["ascii"].mean()
        else:
            for key in [
                "names_count",
                "names_chars_mean",
                "names_chars_median",
                "names_camel_case_ratio",
                "names_snake_case_ratio",
                "names_pascal_case_ratio",
                "names_private_ratio",
                "names_endswith_number_ratio",
                "names_simple_ratio",
                "names_ascii_ratio",
            ]:
                stats_dict[key] = 0

        # Notebook analysis
        total_cells = 0
        total_code_cells = 0
        total_markdown_cells = 0

        for file_path in self.iter_files("ipynb"):
            try:
                nb = Notebook(file_path)
                total_cells += nb.n_cells()
                total_code_cells += nb.n_cells("code")
                total_markdown_cells += nb.n_cells("markdown")
            except Exception:
                continue

        stats_dict["n_cells_total"] = total_cells
        stats_dict["n_cells_code"] = total_code_cells
        stats_dict["n_cells_markdown"] = total_markdown_cells

        # Markdown analysis
        try:
            all_markdown = self.extract("markdown")
            if len(all_markdown) > 0:
                stats_dict["markdown_words_total"] = all_markdown.n_words(total=True)
                stats_dict["markdown_chars_total"] = all_markdown.n_chars(total=True)
                stats_dict["markdown_sentences_total"] = all_markdown.n_sentences(
                    total=True
                )
                stats_dict["markdown_non_ascii_total"] = all_markdown.n_non_ascii(
                    total=True
                )
                stats_dict["markdown_misspelled_total"] = all_markdown.misspelled_words(
                    total=True
                )
            else:
                for key in [
                    "markdown_words_total",
                    "markdown_chars_total",
                    "markdown_sentences_total",
                    "markdown_non_ascii_total",
                    "markdown_misspelled_total",
                ]:
                    stats_dict[key] = 0
        except Exception:
            for key in [
                "markdown_words_total",
                "markdown_chars_total",
                "markdown_non_ascii_total",
                "markdown_sentences_total",
                "markdown_misspelled_total",
            ]:
                stats_dict[key] = np.nan

        return pd.Series(stats_dict, name=dir_name)
