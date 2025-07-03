import ast
import pathlib

from radon.complexity import cc_visit
from radon.raw import analyze
from radon.visitors import Class, Function


class Py:
    """Analyse Python code metrics including lines of code measurements."""

    def __init__(self, source):
        """
        Initialise the Py analyser with Python source code.

        Parameters
        ----------
        source : pathlib.Path or str
            Either a Path object pointing to a Python file or a string containing Python
            code.
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
                if isinstance(node, (ast.Import, ast.ImportFrom)):
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
                        module_name = alias.name.split(".")[0]
                        modules.add(module_name)

                elif isinstance(node, ast.ImportFrom):
                    # Handle: from module import something
                    if node.module:  # Skip relative imports (from . import ...)
                        module_name = node.module.split(".")[0]
                        modules.add(module_name)

            return len(modules)
        except Exception:
            return 0
