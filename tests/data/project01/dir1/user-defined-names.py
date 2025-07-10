import math  # 'math' not included (imported)


class Calculator:  # 'Calculator' included
    def __init__(self, name):  # 'init', 'self', 'name' included
        self.name = name  # 'name' included (attribute)
        self.history = []  # 'history' included (attribute)

    def add(self, x, y):  # 'add', 'self', 'x', 'y' included
        result = x + y + math.pi  # 'result' included
        self.history.append(result)  # 'history' included
        return result


def process_data(data):  # 'process_data', 'data' included
    results = []  # 'results' included

    for item in data:  # 'item' included (loop variable)
        try:
            value = int(item)  # 'value' included
        except ValueError as e:  # 'e' included (exception variable)
            print(f"Error converting {item} to int: {e}")
            value = 0

        results.append(value)

    # List comprehension
    squared = [x**2 for x in results]  # 'squared', 'x' included

    # With statement
    with open("file.txt") as f:  # 'f' included (context variable)
        data = f.read()  # 'data' included

    return squared


# Global variables
counter = 0  # 'counter' included
total_sum = sum([1, 2, 3])  # 'total_sum' included

# Walrus operator
if (n := 6) > 5:  # 'n' included (named expression)
    print(f"Length: {n}")
