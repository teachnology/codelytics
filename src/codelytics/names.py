import re

import pandas as pd


class Names:
    """
    Analyse user-defined names from Python code.

    This class provides functionality to analyse various aspects of user-defined
    names such as variables, function names, class names, and others extracted from
    Python code.

    Parameters
    ----------
    names : Iterable of str
        Set of user-defined names (variables, function names, class names, etc.)
        from Python code.

    Attributes
    ----------
    names : list of str
        The list of user-defined names.
    """

    def __init__(self, names):
        self.names = list(set(names))

    def __len__(self):
        """Return the number of names."""
        return len(self.names)

    @property
    def n_chars(self):
        """
        Return number of characters for each name.

        Returns
        -------
        pd.Series
            Series with name as index and number of characters as values.
        """
        return pd.Series({name: len(name) for name in self.names}, name="n_chars")

    @property
    def camel_case(self):
        """
        Check if names are written in pure camel case.

        Pure camel case means the name starts with a lowercase letter and
        contains uppercase letters for word boundaries (e.g., 'camelCase').

        Returns
        -------
        pd.Series
            Series with name as index and boolean values indicating whether
            the name is in pure camel case.
        """
        camel_pattern = re.compile(r"^[a-z]+(?:[A-Z][a-z]*)*$")
        return pd.Series(
            {name: bool(camel_pattern.match(name)) for name in self.names},
            name="camel_case",
        )

    @property
    def snake_case(self):
        """
        Check if names are written in snake case.

        Snake case means the name uses lowercase letters and underscores
        to separate words (e.g., 'snake_case', 'my_variable').

        Returns
        -------
        pd.Series
            Series with name as index and boolean values indicating whether
            the name is in snake case.
        """
        snake_pattern = re.compile(r"^[a-z]+(?:_[a-z]+)*$")
        return pd.Series(
            {name: bool(snake_pattern.match(name)) for name in self.names},
            name="snake_case",
        )

    @property
    def pascal_case(self):
        """
        Check if names are written in Pascal case.

        Pascal case means the name starts with an uppercase letter and
        contains uppercase letters for word boundaries (e.g., 'PascalCase').

        Returns
        -------
        pd.Series
            Series with name as index and boolean values indicating whether
            the name is in Pascal case.
        """
        pascal_pattern = re.compile(r"^[A-Z][a-z]*(?:[A-Z][a-z]*)*$")
        return pd.Series(
            {name: bool(pascal_pattern.match(name)) for name in self.names},
            name="pascal_case",
        )

    @property
    def private(self):
        """
        Check if names are private variables.

        Private variables are those that start with an underscore
        (e.g., '_private', '__dunder__').

        Returns
        -------
        pd.Series
            Series with name as index and boolean values indicating whether
            the name is a private variable.
        """
        private_pattern = re.compile(r"^_")
        return pd.Series(
            {name: bool(private_pattern.match(name)) for name in self.names},
            name="private",
        )

    @property
    def endswith_number(self):
        """
        Check if names end with a number.

        Returns true if the variable name ends with a digit (0-9).

        Returns
        -------
        pd.Series
            Series with name as index and boolean values indicating whether
            the name ends with a number.
        """
        number_pattern = re.compile(r"\d$")
        return pd.Series(
            {name: bool(number_pattern.search(name)) for name in self.names},
            name="endswith_number",
        )

    @property
    def simple(self):
        """
        Check if names are simple (one word, all lowercase letters).

        Simple names contain only lowercase letters with no underscores,
        numbers, or uppercase letters (e.g., 'x', 'total', 'result').

        Returns
        -------
        pd.Series
            Series with name as index and boolean values indicating whether
            the name is simple.
        """
        simple_pattern = re.compile(r"^[a-z]+$")
        return pd.Series(
            {name: bool(simple_pattern.match(name)) for name in self.names},
            name="simple",
        )

    @property
    def ascii(self):
        """
        Check if names contain only ASCII characters.

        Returns true if the variable name contains only characters within
        the ASCII range (0-127).

        Returns
        -------
        pd.Series
            Series with name as index and boolean values indicating whether
            the name contains only ASCII characters.
        """
        ascii_pattern = re.compile(r"^[\x00-\x7F]*$")
        return pd.Series(
            {name: bool(ascii_pattern.match(name)) for name in self.names}, name="ascii"
        )

    @property
    def stats(self):
        """
        Get statistics about the user-defined names.

        Returns
        -------
        pd.DataFrame
            DataFrame with various statistics about the names, including:
            - Number of characters
            - Camel case
            - Snake case
            - Pascal case
            - Private
            - Ends with number
            - ASCII
        """
        return pd.concat(
            [
                self.n_chars,
                self.camel_case,
                self.snake_case,
                self.pascal_case,
                self.private,
                self.endswith_number,
                self.simple,
                self.ascii,
            ],
            axis=1,
        )
