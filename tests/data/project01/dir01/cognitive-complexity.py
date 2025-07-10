# Total complexity: 1
data = [1, 2, 3, 4, 5]
for d in data:  # +1
    print(d)


def simple_function():  # Total complexity: 0
    print("Hello, world!")


def medium_complexity(x):  # Total complexity: 1
    if x > 10:  # +1
        print("Large number")
    elif x > 5:  # +0
        print("Medium number")
    else:
        print("Small number")


def high_complexity(x):  # Total complexity: 6
    for i in range(x):  # +1
        if i % 2 == 0:  # +1 +1 (nested)
            if i % 3 == 0:  # +1 +1 +1 (deeper nesting)
                print("Divisible by 6")
            else:
                print("Even")
        else:
            print("Odd")


class ExampleClass:
    def method_with_zero_complexity(self):
        return 42  # Just a return; complexity: 0

    def method_with_complexity_three(self, items):  # Total complexity: 6
        for item in items:  # +1
            if isinstance(item, int):  # +1 +1 (nested)
                if item > 0:  # +1 +1 +1 (deeper nesting)
                    print("Positive int")
