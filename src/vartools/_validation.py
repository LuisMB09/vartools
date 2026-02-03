"""Internal validation helpers."""


def _validate_confidence(value, name="conf"):
    """
    Validate that a confidence level is between 0 and 100 (exclusive).

    Parameters
    ----------
    value : int | float
        The confidence level to validate.
    name : str
        The parameter name for error messages.

    Raises
    ------
    ValueError
        If value is not in the valid range.
    """
    if not (0 < value < 100):
        raise ValueError(f"{name} must be between 0 and 100 (exclusive), got {value}")
