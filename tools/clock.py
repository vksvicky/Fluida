"""Hour and minute fill fractions from the Fluida spec."""


def display_hour(hour: int) -> int:
    """Map 0..23 onto the 1..12 column."""
    shown = hour % 12
    return 12 if shown == 0 else shown


def hour_fill(hour: int) -> float:
    """1 sits on the bottom mark. 12 fills the column."""
    return (display_hour(hour) - 1) / 11


def minute_fill(minute: int, second: int) -> float:
    """Continuous fill across the current minute. Stays below 1 at 59:59."""
    return (minute + second / 60) / 60
