def simple():  # complexity = 1
    return 1


def complex_func(x):  # complexity = 3
    if x > 0:
        if x > 10:
            return "high"
        return "medium"
    return "low"


class MyClass:
    def method(self):  # complexity = 1
        return "hello"

    def complex_method(self, x):  # complexity = 2
        if x:
            return "yes"
        return "no"
