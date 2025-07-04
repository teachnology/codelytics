def simple():  # 0
    return 1


def complex_nested(x):  # Higher cognitive complexity due to nesting
    if x > 0:  # +1 (base increment for if)
        for i in range(x):  # +2 (base increment +1, nesting increment +1)
            if i % 2 == 0:  # +3 (base increment +1, nesting increment +2)
                print(i)
    return x


class MyClass:
    def method(self):  # Simple method
        return 1 + 2
