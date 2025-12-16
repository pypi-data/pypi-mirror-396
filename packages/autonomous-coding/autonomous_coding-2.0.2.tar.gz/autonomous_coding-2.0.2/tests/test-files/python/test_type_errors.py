"""Test file with intentional type errors for testing TypeCheckGate."""


def add_numbers(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


def process_data(items: list[str]) -> None:
    """Process a list of strings."""
    for item in items:
        print(item)


# Type errors that Mypy should catch:
result = add_numbers("hello", "world")  # Type error: str instead of int
process_data([1, 2, 3])  # Type error: List[int] instead of List[str]


def incompatible_return() -> str:
    """Function with incompatible return type."""
    return 123  # Type error: int instead of str
