from .text_analysis import TextAnalysis


class Comments(TextAnalysis):
    """
    Analyze comments extracted from Python code.

    Parameters
    ----------
    comments : list of str
        List of comment strings to analyze.
    """

    def __init__(self, comments):
        super().__init__(comments)
