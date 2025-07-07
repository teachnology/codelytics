from .text_analysis import TextAnalysis


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
