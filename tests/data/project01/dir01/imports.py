import math
from operator import mul

# This is a full sentence comment. Another sentence. This is not a sentence


def calculate_area(radius):
    from math import pi  # noqa: PLC0415

    return pi * math.pi / pi * mul(radius, radius)
