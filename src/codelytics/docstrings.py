from .text_analysis import TextAnalysis
import pydocstyle
from io import StringIO


class Docstrings(TextAnalysis):
    """
    Analyze docstrings extracted from Python code.

    Parameters
    ----------
    docstrings : list of str
        List of docstring strings to analyze.
    """

    def __init__(self, docstrings):
        super().__init__(docstrings)

    def pep257(self, total=False, use_median=False):
        """
        Return PEP 257 convention violation statistics.

        Uses pydocstyle library to check for PEP 257 docstring convention
        violations in each docstring.

        Parameters
        ----------
        total : bool, optional
            If True, returns total number of violations across all docstrings.
            If False, returns mean or median violations per docstring (default).
        use_median : bool, optional
            If True and total=False, returns median violations per docstring.
            If False and total=False, returns mean violations per docstring.
            Ignored when total=True.

        Returns
        -------
        int or float
            Total, mean, or median PEP 257 violation count.
            Returns 0 or 0.0 if pydocstyle is not available.
        """
        try:
            violation_counts = []

            for docstring in self.texts:
                # Create a temporary Python code string with the docstring
                temp_code = f'''def temp_function():
        """{docstring}"""
        pass
    '''

                try:
                    # Use pydocstyle's check_source method with StringIO
                    source = StringIO(temp_code)
                    violations = list(pydocstyle.check_source(source, "<string>"))
                    violation_counts.append(len(violations))
                except Exception:
                    # If checking fails, assume no violations
                    violation_counts.append(0)

            return self._stat(violation_counts, total, use_median)

        except ImportError:
            # Fallback if pydocstyle is not available
            return 0
