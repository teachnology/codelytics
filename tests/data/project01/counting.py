import collections
import math

import pandas as pd
from numpy import array


def calculate_statistics(data):
    """Calculate basic statistics for a dataset."""
    return {
        "mean": sum(data) / len(data),
        "max": max(data),
        "min": min(data),
        "count": len(data),
    }


def process_data(values):
    """Process and transform data values."""
    arr = array(values)
    return arr * 2 + math.pi


class DataAnalyzer:
    def __init__(self, data):
        self.data = data
        self.counter = collections.Counter()

    def analyze(self):
        """Analyze the data and return insights."""
        self.counter.update(self.data)
        return self.counter.most_common(3)

    def to_dataframe(self):
        """Convert data to pandas DataFrame."""
        return pd.DataFrame({"values": self.data})

    def get_summary(self):
        """Get summary statistics."""
        sh = self.to_dataframe()
        return sh.describe()


class MathProcessor:
    def __init__(self, precision=2):
        self.precision = precision
        self.results = []

    def square_root(self, number):
        """Calculate square root with specified precision."""
        from math import sqrt  # noqa: PLC0415

        result = round(sqrt(number), self.precision)
        self.results.append(result)
        return result

    def clear_results(self):
        """Clear stored results."""
        self.results.clear()

    def get_results_array(self):
        """Return results as numpy array."""
        return array(self.results)

    def logarithm(self, number, base=math.e):
        """Calculate logarithm with specified base.

        Parameters
        ----------
        number : float
            The number to calculate the logarithm for.
        base : float, optional
            The base of the logarithm (default is e).

        Returns
        -------
        float
            The logarithm of the number to the specified base.
        """
        result = round(math.log(number, base), self.precision)
        self.results.append(result)
        return result
