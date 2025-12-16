"""frequency utils"""

# see https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases

import re

PANDAS_FREQ = dict(day="B", week="W", month="ME", year="Y", hour="H", minute="min")


def base_frequency(freq: str, drop_count=True) -> str:
    """maps freq string to base frequency: day, hour, minute, ..."""

    if drop_count:
        if match := re.fullmatch(r"\d+(\w+)", freq):
            freq = match.group(1)

    if freq in ("D", "day", "daily"):
        freq = "day"
    elif freq in ("W", "week", "weekly"):
        freq = "week"
    elif freq in ("M", "month", "monthly"):
        freq = "month"
    elif freq in ("Y", "year", "yearly"):
        freq = "year"
    elif freq in ("H", "hour", "hourly"):
        freq = "hour"
    elif freq in ("T", "min", "minute"):
        freq = "minute"
    else:
        raise ValueError(f"Invalid freq {freq!r}")

    return freq


def split_frequency(freq: str) -> tuple:
    """split freq string into count and frequency name: day, hour, minute ..."""

    if match := re.fullmatch(r"(\d+)(\w+)", freq):
        count, freq = int(match.group(1)), match.group(2)
    elif match := re.fullmatch(r"(\w+)", freq):
        count, freq = 1, match.group(1)
    else:
        raise ValueError(f"Invalid freq {freq!r}")

    freq = base_frequency(freq, drop_count=False)

    return count, freq


def pandas_freq(freq: str) -> str:
    """map a frequency string to a pandas frequency string"""

    count, freq = split_frequency(freq)
    freq = PANDAS_FREQ.get(freq)

    if count != 1:
        freq = f"{count}{freq}"

    return freq
