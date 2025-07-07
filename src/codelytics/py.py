import ast
import pathlib
import tokenize
import io

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

    def cc(self, total=False, use_median=False):
        """
        Return cyclomatic complexity statistics.

        Calculate either total cyclomatic complexity for the entire source or
        mean/median complexity per function.

        Parameters
        ----------
        total : bool, optional
            If True, returns total cyclomatic complexity for entire source.
            If False, returns mean or median complexity per function (default).
        use_median : bool, optional
            If True and total=False, returns median complexity per function.
            If False and total=False, returns mean complexity per function.
            Ignored when total=True.

        Returns
        -------
        int or float
            If total=True: Total cyclomatic complexity (int).
            If total=False: Mean or median complexity per function (float).
            Returns 0 or 0.0 if parsing fails or no functions found.
        """
        try:
            results = cc_visit(self.content)

            if total:
                return sum(item.complexity for item in results)
            else:
                # Per-function statistics
                complexities = [
                    item.complexity for item in results if isinstance(item, Function)
                ]

                if not complexities:
                    return 0.0

                if use_median:
                    return float(pd.Series(complexities).median())
                else:
                    return float(pd.Series(complexities).mean())

        except Exception:
            return 0 if total else 0.0

    def cogc(self, total=False, use_median=False):
        """
        Return cognitive complexity statistics.

        Cognitive complexity measures how difficult code is to understand by humans,
        focusing on readability rather than testability. Can return total complexity
        for entire source or mean/median complexity per function.

        Based on complexipy.

        Parameters
        ----------
        total : bool, optional
            If True, returns total cognitive complexity for entire source.
            If False, returns mean or median complexity per function (default).
        use_median : bool, optional
            If True and total=False, returns median cognitive complexity per function.
            If False and total=False, returns mean cognitive complexity per function.
            Ignored when total=True.

        Returns
        -------
        int or float
            If total=True: Total cognitive complexity (int).
            If total=False: Mean or median complexity per function (float).
            Returns 0 or 0.0 if no functions found or if complexipy is not available.
        """
        try:
            result = complexipy.code_complexity(self.content)

            if total:
                return result.complexity

            # Extract individual function complexities
            if hasattr(result, "functions") and result.functions:
                complexities = [func.complexity for func in result.functions]
            else:
                return 0

            if not complexities:
                return 0

            if use_median:
                return float(pd.Series(complexities).median())
            else:
                return float(pd.Series(complexities).mean())

        except Exception:
            return 0 if total else 0.0

    def halstead(self, total=False, use_median=False):
        """
        Return Halstead complexity metrics.

        Halstead metrics measure program complexity based on the number of
        operators and operands in the code. Can return total metrics for entire
        source or mean/median values per function.

        Parameters
        ----------
        total : bool, optional
            If True, returns total Halstead metrics for entire source including
            all code. If False, returns mean or median metrics per function (default).
        use_median : bool, optional
            If True and total=False, returns median Halstead metrics per function.
            If False and total=False, returns mean Halstead metrics per function.
            Ignored when total=True.

        Returns
        -------
        pandas.Series
            Series with Halstead metrics as values and metric names as index:
            - 'vocabulary' (n): Program vocabulary (n1 + n2)
            - 'length' (N): Program length (N1 + N2)
            - 'volume' (V): Program volume (N * log2(n))
            - 'difficulty' (D): Program difficulty (n1/2 * N2/n2)
            - 'effort' (E): Program effort (D * V)

            If total=True: Total metrics for entire source.
            If total=False: Mean or median metrics per function.
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
            halstead_data = h_visit(self.content)

            if total:
                # Get total metrics for entire source
                total_report = halstead_data.total
                return pd.Series(
                    {
                        "vocabulary": float(total_report.vocabulary),
                        "length": float(total_report.length),
                        "volume": float(total_report.volume),
                        "difficulty": float(total_report.difficulty),
                        "effort": float(total_report.effort),
                    }
                )
            else:
                # Per-function statistics
                if not halstead_data.functions:
                    return zero_series

                # Get HalsteadReport objects for each function
                function_reports = [report for _, report in halstead_data.functions]

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

    def user_defined_names(self):
        """
        Return all user-defined names in the source code.

        Extracts all identifiers that are defined by the user, including variable names,
        function names, class names, parameter names, attributes, and other identifiers.
        Excludes built-in names, imported names, and standard library identifiers.

        Returns
        -------
        list
            Sorted list of unique user-defined names found in the source code.
            Returns empty list if parsing fails.
        """
        try:
            tree = ast.parse(self.content)
            user_names = set()

            for node in ast.walk(tree):
                # Function definitions
                if isinstance(node, (ast.FunctionDef | ast.AsyncFunctionDef)):
                    user_names.add(node.name)
                    # Function parameters
                    for arg in node.args.args:
                        user_names.add(arg.arg)
                    for arg in node.args.posonlyargs:
                        user_names.add(arg.arg)
                    for arg in node.args.kwonlyargs:
                        user_names.add(arg.arg)
                    if node.args.vararg:
                        user_names.add(node.args.vararg.arg)
                    if node.args.kwarg:
                        user_names.add(node.args.kwarg.arg)

                # Class definitions
                elif isinstance(node, ast.ClassDef):
                    user_names.add(node.name)

                # Variable assignments
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            user_names.add(target.id)
                        elif isinstance(target, ast.Tuple | ast.List):
                            for elt in target.elts:
                                if isinstance(elt, ast.Name):
                                    user_names.add(elt.id)
                        elif isinstance(target, ast.Attribute):
                            # Class attributes (self.attr = value)
                            user_names.add(target.attr)

                # Augmented assignments (+=, -=, etc.)
                elif isinstance(node, ast.AugAssign):
                    if isinstance(node.target, ast.Name):
                        user_names.add(node.target.id)
                    elif isinstance(node.target, ast.Attribute):
                        user_names.add(node.target.attr)

                # Annotated assignments (var: type = value)
                elif isinstance(node, ast.AnnAssign):
                    if isinstance(node.target, ast.Name):
                        user_names.add(node.target.id)
                    elif isinstance(node.target, ast.Attribute):
                        user_names.add(node.target.attr)

                # Named expressions (walrus operator :=)
                elif isinstance(node, ast.NamedExpr):
                    if isinstance(node.target, ast.Name):
                        user_names.add(node.target.id)

                # For loop variables
                elif isinstance(node, ast.For):
                    if isinstance(node.target, ast.Name):
                        user_names.add(node.target.id)
                    elif isinstance(node.target, ast.Tuple | ast.List):
                        for elt in node.target.elts:
                            if isinstance(elt, ast.Name):
                                user_names.add(elt.id)

                # Comprehension variables
                elif isinstance(
                    node, (ast.ListComp | ast.SetComp | ast.DictComp | ast.GeneratorExp)
                ):
                    for generator in node.generators:
                        if isinstance(generator.target, ast.Name):
                            user_names.add(generator.target.id)
                        elif isinstance(generator.target, ast.Tuple | ast.List):
                            for elt in generator.target.elts:
                                if isinstance(elt, ast.Name):
                                    user_names.add(elt.id)

                # Exception handling variables
                elif isinstance(node, ast.ExceptHandler):
                    if node.name:
                        user_names.add(node.name)

                # With statement variables
                elif isinstance(node, ast.withitem):
                    if node.optional_vars:
                        if isinstance(node.optional_vars, ast.Name):
                            user_names.add(node.optional_vars.id)
                        elif isinstance(node.optional_vars, ast.Tuple | ast.List):
                            for elt in node.optional_vars.elts:
                                if isinstance(elt, ast.Name):
                                    user_names.add(elt.id)

                # Global and nonlocal declarations
                elif isinstance(node, ast.Global):
                    for name in node.names:
                        user_names.add(name)
                elif isinstance(node, ast.Nonlocal):
                    for name in node.names:
                        user_names.add(name)

            return {
                name
                for name in user_names - {"self", "cls"}
                if not name.startswith("__") and not name.endswith("__")
            }  # Exclude common names

        except Exception:
            return set()

    def comments(self):
        """
        Return all comments found in the source code.

        Extracts all single-line (#) and multi-line comments from the Python source.
        Excludes docstrings (triple-quoted strings used as documentation).

        Returns
        -------
        list of str
            List of comment strings with leading # and whitespace stripped.
            Returns empty list if parsing fails or no comments found.
        """
        try:
            comments = []
            tokens = tokenize.generate_tokens(io.StringIO(self.content).readline)

            for token in tokens:
                if token.type == tokenize.COMMENT:
                    # Strip the # and any leading/trailing whitespace
                    comment_text = token.string.lstrip("#").strip()
                    if comment_text:  # Only add non-empty comments
                        comments.append(comment_text)

            return comments

        except Exception:
            return []

    def docstrings(self):
        """
        Return all docstrings found in the source code.

        Extracts docstrings from modules, classes, functions, and methods.
        A docstring is the first string literal in a module, class, or function body.

        Returns
        -------
        list of str
            List of docstring contents with leading/trailing whitespace stripped.
            Returns empty list if parsing fails or no docstrings found.
        """
        try:
            tree = ast.parse(self.content)
            docstrings = []

            def extract_docstring(node):
                """Extract docstring from a node if it exists."""
                if (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)
                ):
                    return node.body[0].value.value.strip()
                return None

            # Module docstring
            module_docstring = extract_docstring(tree)
            if module_docstring:
                docstrings.append(module_docstring)

            # Walk through all nodes to find classes and functions
            for node in ast.walk(tree):
                if isinstance(
                    node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                ):
                    docstring = extract_docstring(node)
                    if docstring:
                        docstrings.append(docstring)

            return docstrings

        except Exception:
            return []
