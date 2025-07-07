def add(x, y):
    return x + y


def multiply(a, b):
    result = a * b
    return result


class Calculator:
    def divide(self, x, y):
        if y != 0:
            return x / y
        return None


x = 3
y = 5
print(x + y)
