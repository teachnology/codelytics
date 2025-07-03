import pathlib
from radon.raw import analyze
from radon.complexity import cc_visit
from radon.visitors import Function, Class


class Py:
    """Analyse Python code metrics including lines of code measurements."""

    def __init__(self, source):
        """
        Initialise the Py analyser with Python source code.

        Parameters
        ----------
        source : pathlib.Path or str
            Either a Path object pointing to a Python file or a string containing Python code.
        """
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
        comments, and code lines.

        Returns
        -------
        int
            Number of physical lines of code.
        """
        try:
            module = analyze(self.content)
            return module.loc
        except Exception:
            # Fallback for any parsing errors
            return len(self.content.splitlines())

    def lloc(self):
        """
        Return the number of logical lines of code.

        Logical lines of code represents the number of executable statements.
        This uses Radon's analysis to count actual Python statements.

        Returns
        -------
        int
            Number of logical lines of code.
        """
        try:
            module = analyze(self.content)
            return module.lloc
        except Exception:
            return 0

    def sloc(self):
        """
        Return the number of source lines of code.

        Source lines of code excludes blank lines, comments, and docstrings.
        Only actual executable code lines are counted.

        Returns
        -------
        int
            Number of source lines of code.
        """
        try:
            module = analyze(self.content)
            return module.sloc
        except Exception:
            return 0

    def n_char(self):
        """
        Return the number of characters in the Python code.

        Returns
        -------
        int
            Total number of characters including whitespace and newlines.
        """
        return len(self.content)

    def n_functions(self):
        """
        Return the number of functions in the Python code.

        Counts function definitions including regular functions, async functions,
        methods, static methods, class methods, and nested functions.

        Returns
        -------
        int
            Total number of function definitions.
        """
        try:
            results = cc_visit(self.content)
            # Count only Function objects, excluding Class objects
            function_count = sum(1 for item in results if isinstance(item, Function))
            return function_count
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
            class_count = sum(1 for item in results if isinstance(item, Class))
            return class_count
        except Exception:
            return 0
