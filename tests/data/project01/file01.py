import operator


def add(x, y):
    return operator.add(x, y)  # Comment


def subtract(x, y):
    """Subtracts two numbers.

    Parameters
    ----------
    x : int or float
        The first operand.
    y : int or float
        The second operand.
    """
    return operator.sub(x, y)
