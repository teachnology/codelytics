# Block comment 1
# Block comment 2


def hello(name):
    """Returns a greeting message.

    Further explanation of the function.

    Parameters
    ----------
    name : str
        The name of the person to greet.
    """
    return (
        f"Hello, "
        f"{name}!"  # inline comment
    )


if __name__ == "__main__":
    print(hello("世界"))  # inline comment


# Footer comment 1
