"""Module docstring
with multiple lines"""

a = [
    "This is sentence 1.",
    "This is sentence 2.",
    "This is sentence 3.",
    "This is sentence 4.",
]


# Comment line
def function_one():
    """Function docstring."""
    x = 1
    if x > 0:
        return x  # inline comment
    else:
        return 0


class TestClass:
    """Class docstring."""

    def method(self):
        # Inline comment
        pass


# Another comment
def function_two():
    for i in range(3):
        print(i)
