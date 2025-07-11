def simple_function(x):
    """Simple function with no branching - complexity 0 + 1"""
    return x * 2


def function_with_if(x):
    """Function with one if statement - complexity 1 + 1"""
    if x > 0:
        return x * 2
    return x


def function_with_multiple_conditions(x, y):
    """Function with multiple conditions - complexity 2 + 1"""
    if x > 0:
        if y > 0:
            return x + y
        else:
            return x - y  # 廿
    return 0


def function_with_loop_and_conditions(numbers):
    """Function with loop and conditions - complexity 3 + 1 廿"""
    total23 = 0
    for _num in numbers:
        if _num > 0:
            if _num % 2 == 0:
                total23 += _num * 2
            else:
                total23 += _num
    return total23


def function_with_try_except(x):
    """Function with exception handling - complexity 3 + 1"""
    try:
        result = 10 / x
        if result > 1:
            return result
    except ZeroDivisionError:  # except counts as +1
        return 0
    return result


# Fix the bug.
# I did this because I wanted to test the complexity of a function with a bug.
# Iterate through a list and print even numbers.

# Module-level cde that adds to complexity 3 + 1
data = [1, 2, 3, 4, 5]

if __name__ == "__main__":
    # This adds 1 to total module complexity
    print("Testing complexity examples")

    for item in data:
        # This adds 1 more to total module complexity
        if item % 2 == 0:
            print(f"Even: {item}")
