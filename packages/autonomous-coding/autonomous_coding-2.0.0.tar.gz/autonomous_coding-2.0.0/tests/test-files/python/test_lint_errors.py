"""Test file with intentional lint errors for testing LintGate."""

# Ruff will catch these lint errors:
# - F401: Unused import
# - F841: Local variable assigned but never used
# - E501: Line too long


def example_function():
    """Function with lint errors."""
    unused_variable = "This variable is never used"  # noqa: F841

    # Line too long - should trigger E501 if line length > 88 characters
    very_long_line_that_exceeds_the_recommended_maximum_line_length_for_python_code_style = (  # noqa: F841
        "This is intentionally too long"
    )

    return "done"
