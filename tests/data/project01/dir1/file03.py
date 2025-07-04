import math
from operator import mul


def calculate_area(radius):
    from math import pi  # noqa: PLC0415

    return pi * math.pi / pi * mul(radius, radius)
