"""Test file with intentionally failing unit tests for testing UnitTestGate."""


def add(a, b):
    """Add two numbers."""
    return a + b


def multiply(a, b):
    """Multiply two numbers."""
    return a * b


# Passing test
def test_add_positive_numbers():
    """Test adding positive numbers."""
    assert add(2, 3) == 5


# Failing test - intentional error
def test_add_negative_numbers():
    """Test adding negative numbers - INTENTIONALLY FAILS."""
    assert add(-2, -3) == -4  # Wrong: should be -5


# Failing test - intentional error
def test_multiply():
    """Test multiplication - INTENTIONALLY FAILS."""
    assert multiply(3, 4) == 13  # Wrong: should be 12


# Passing test
def test_multiply_by_zero():
    """Test multiplying by zero."""
    assert multiply(5, 0) == 0
