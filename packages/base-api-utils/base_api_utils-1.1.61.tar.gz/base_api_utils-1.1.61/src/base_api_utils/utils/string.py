from datetime import datetime, time


def is_empty(str_val: str) -> bool:
    return not str_val or not (str_val and str_val.strip())

def safe_str_to_number(value):
    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        pass

    raise ValueError(f"'{value}' is not a valid number.")

def to_comma_separated(value) -> str:
    """
    Converts a value to a comma-separated string.

    Args:
        value: can be int, str, list[int], list[str], or None

    Returns:
        String with comma-separated values
    """
    if value is None:
        return ""

    if isinstance(value, (list, tuple)):
        return ",".join(str(item) for item in value)

    return str(value)

def from_comma_separated(value: str):
    """
    Converts a comma-separated string back to its original type.

    Args:
        value: String with comma-separated values

    Returns:
        - Empty string returns None
        - Single value returns int (if numeric) or str
        - Multiple values return list[int] (if all numeric) or list[str]
    """
    if not value:
        return None

    # Split by comma
    parts = [part.strip() for part in value.split(",")]

    # Single value case
    if len(parts) == 1:
        try:
            return int(parts[0])
        except ValueError:
            return parts[0]

    return parts

def is_valid_time(s: str) -> bool:
    try:
        time.fromisoformat(s)
        return True
    except ValueError:
        return False

def is_valid_datetime(s: str) -> bool:
    try:
        datetime.fromisoformat(s)
        return True
    except ValueError:
        return False