import ast
import pathlib

import complexipy

import pandas as pd
from radon.complexity import cc_visit
from radon.metrics import h_visit
from radon.raw import analyze
from radon.visitors import Class, Function


class Py:
    """Analyse Python code metrics.

    Parameters
    ----------
    source : pathlib.Path or str
        Either a Path object pointing to a Python file or a string containing Python
        code.

    """

    def __init__(self, source):
        if isinstance(source, pathlib.Path):
            if not source.exists():
                raise FileNotFoundError(f"Python file not found: {source}")
            if not source.suffix == ".py":
                raise ValueError(f"File must have .py extension: {source}")
            self.content = source.read_text(encoding="utf-8")
        elif isinstance(source, str):
            self.content = source
        else:
            raise TypeError("Source must be a pathlib.Path object or string")

    def loc(self):
        """
        Return the number of physical lines of code.

        Physical lines of code includes all lines in the file including blank lines,
        comments, docstrings, and code lines.

        Returns
        -------
        int
            Number of physical lines of code.
        """
        try:
            return analyze(self.content).loc
        except Exception:
            # Fallback for any parsing errors
            return len(self.content.splitlines())

    def lloc(self):
        """
        Return the number of logical lines of code.

        Logical lines of code represents the number of executable statements. This uses
        Radon's analysis to count actual Python statements. It includes docstrings, but
        excludes comments and blank lines.

        If the content cannot be parsed, it returns 0.

        Returns
        -------
        int
            Number of logical lines of code.
        """
        try:
            return analyze(self.content).lloc
        except Exception:
            return 0

    def sloc(self):
        """
        Return the number of source lines of code.

        Source lines of code excludes blank lines, comments, and docstrings. Only actual
        executable code lines are counted. Command continuation lines are counted as
        multiple lines.

        If the content cannot be parsed, it returns 0.

        Returns
        -------
        int
            Number of source lines of code.
        """
        try:
            return analyze(self.content).sloc
        except Exception:
            return 0

    def n_char(self):
        """
        Return the number of characters.

        Returns
        -------
        int
            Total number of characters including whitespace and newlines.
        """
        return len(self.content)

    def n_functions(self):
        """
        Return the number of functions.

        Counts function definitions including regular functions, async functions,
        methods, static methods, class methods, and nested functions.

        If the content cannot be parsed, it returns 0.

        Returns
        -------
        int
            Total number of function definitions.
        """
        try:
            results = cc_visit(self.content)
            # Count only Function objects, excluding Class objects
            return sum(1 for item in results if isinstance(item, Function))
        except Exception:
            return 0

    def n_classes(self):
        """
        Return the number of classes in the Python code.

        Counts class definitions including regular classes, nested classes,
        and classes with inheritance.

        Returns
        -------
        int
            Total number of class definitions.
        """
        try:
            results = cc_visit(self.content)
            # Count only Class objects, excluding Function objects
            return sum(1 for item in results if isinstance(item, Class))
        except Exception:
            return 0

    def n_imports(self):
        """
        Return the number of import statements in the Python code.

        Counts all types of import statements including:
        - import module
        - from module import function
        - import module as alias
        - from module import function as alias
        - from module import *

        Returns
        -------
        int
            Total number of import statements.
        """
        try:
            tree = ast.parse(self.content)
            import_count = 0

            for node in ast.walk(tree):
                if isinstance(node, ast.Import | ast.ImportFrom):
                    import_count += 1

            return import_count
        except Exception:
            return 0

    def n_imported_modules(self):
        """
        Return the number of unique modules imported in the Python code.

        Counts unique top-level modules/packages that are imported, regardless
        of how many times they appear or what is imported from them.
        - import os, sys → 2 modules
        - import os.path, os.environ → 1 module (os)
        - from pathlib import Path; import pathlib → 1 module (pathlib)
        - from . import local → 0 modules (relative import)

        If the content cannot be parsed, it returns 0.

        Returns
        -------
        int
            Total number of unique modules imported.
        """
        try:
            tree = ast.parse(self.content)
            modules = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    # Handle: import module, import module.submodule
                    for alias in node.names:
                        modules.add(alias.name.split(".")[0])

                elif isinstance(node, ast.ImportFrom):
                    # Handle: from module import something
                    if node.module:  # Skip relative imports (from . import ...)
                        modules.add(node.module.split(".")[0])

            return len(modules)
        except Exception:
            return 0

    def cc_stats(self, use_median=False):
        """
        Return the mean or median cyclomatic complexity per function.

        Calculates complexity statistics for individual functions and methods,
        including class methods, static methods, and regular functions.

        Parameters
        ----------
        use_median : bool, optional
            If True, returns median complexity per function.
            If False, returns mean complexity per function (default).

        Returns
        -------
        float
            Mean or median cyclomatic complexity per function.
            Returns 0.0 if no functions are found.
        """
        try:
            complexities = [
                item.complexity
                for item in cc_visit(self.content)
                if isinstance(item, Function)
            ]

            if not complexities:
                return 0.0

            if use_median:
                return float(pd.Series(complexities).median())
            else:
                return float(pd.Series(complexities).mean())
        except Exception:
            return 0.0

    def cogc_stats(self, use_median=False):
        """
        Return the mean or median cognitive complexity per function.

        Cognitive complexity measures how difficult code is to understand by humans,
        focusing on readability rather than testability. Includes all functions
        and methods (regular functions, class methods, static methods, etc.).

        Based on complexipy.

        Parameters
        ----------
        use_median : bool, optional
            If True, returns median cognitive complexity per function.
            If False, returns mean cognitive complexity per function (default).

        Returns
        -------
        float
            Mean or median cognitive complexity per function.
            Returns 0.0 if no functions are found or if complexipy is not available.
        """
        try:
            result = complexipy.code_complexity(self.content)

            # Extract individual function complexities
            if hasattr(result, "functions") and result.functions:
                complexities = [func.complexity for func in result.functions]
            else:
                return 0.0

            if not complexities:
                return 0.0

            if use_median:
                return float(pd.Series(complexities).median())
            else:
                return float(pd.Series(complexities).mean())

        except Exception:
            return 0.0

    def halstead_stats(self, use_median=False):
        """
        Return Halstead complexity metrics as a pandas Series.

        Halstead metrics measure program complexity based on the number of
        operators and operands in the code. Can return mean or median values
        per function.

        Parameters
        ----------
        use_median : bool, optional
            If True, returns median Halstead metrics per function.
            If False, returns mean Halstead metrics per function (default).

        Returns
        -------
        pandas.Series
            Series with Halstead metrics as values and metric names as index:
            - 'vocabulary' (n): Program vocabulary (n1 + n2)
            - 'length' (N): Program length (N1 + N2)
            - 'volume' (V): Program volume (N * log2(n))
            - 'difficulty' (D): Program difficulty (n1/2 * N2/n2)
            - 'effort' (E): Program effort (D * V)

            Returns Series with zeros if no functions found or parsing fails.
        """
        zero_series = pd.Series(
            {
                "vocabulary": 0.0,
                "length": 0.0,
                "volume": 0.0,
                "difficulty": 0.0,
                "effort": 0.0,
            }
        )

        try:
            # print(function_reports)
            halstead_data = h_visit(self.content)

            # Extract per-function metrics
            if not halstead_data.functions:
                return zero_series

            # Get HalsteadReport objects for each function
            function_reports = [report for _, report in halstead_data.functions]

            print(1000*"-")
            print(function_reports)

            # Extract metric arrays
            vocabularies = [report.vocabulary for report in function_reports]
            lengths = [report.length for report in function_reports]
            volumes = [report.volume for report in function_reports]
            difficulties = [report.difficulty for report in function_reports]
            efforts = [report.effort for report in function_reports]

            # Calculate mean or median using pandas
            if use_median:
                return pd.Series(
                    {
                        "vocabulary": float(pd.Series(vocabularies).median()),
                        "length": float(pd.Series(lengths).median()),
                        "volume": float(pd.Series(volumes).median()),
                        "difficulty": float(pd.Series(difficulties).median()),
                        "effort": float(pd.Series(efforts).median()),
                    }
                )
            else:
                return pd.Series(
                    {
                        "vocabulary": float(pd.Series(vocabularies).mean()),
                        "length": float(pd.Series(lengths).mean()),
                        "volume": float(pd.Series(volumes).mean()),
                        "difficulty": float(pd.Series(difficulties).mean()),
                        "effort": float(pd.Series(efforts).mean()),
                    }
                )

        except Exception:
            return zero_series
