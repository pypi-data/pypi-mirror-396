"""utility routines"""

import re

import datetime as dt


MINDATE = dt.date(1970, 1, 1)


def map_frequency(freq):
    """map frequency string to multiplier, timespan"""

    match = re.fullmatch(r"(\d+)(\w+)", freq)

    if match:
        multiplier = int(match.group(1))
        freq = match.group(2)
    else:
        multiplier = 1

    if freq in ("sec", "second"):
        timespan = "second"
    elif freq in ("min", "minute"):
        timespan = "minute"
    elif freq in ("hour", "hourly"):
        timespan = "hour"
    elif freq in ("day", "daily"):
        timespan = "day"
    elif freq in ("week", "weekly"):
        timespan = "week"
    elif freq in ("month", "monthly"):
        timespan = "month"
    else:
        raise ValueError(f"Invalid frequency {freq}!")

    return multiplier, timespan



def days_equivalent(freq: str, periods: int):
    """days equivalent for number of periods of given frequency (business days)"""

    multiplier, timespan = map_frequency(freq)

    match timespan:
        case "second":
            factor = 1 / 23400
        case "minute":
            factor = 1 / 390
        case "hour":
            factor = 1 / 6.5
        case "day":
            factor = 1
        case "week":
            factor = 5
        case "month":
            factor = 22
        case _:
            raise ValueError("Invalid timespan {timespan!r}")

    daycount = periods * multiplier * factor

    if daycount > 10000:
        daycount = 10000

    return daycount



def fix_dates(start_date, end_date, *, freq: str, periods: int = None):
    """fix dates"""

    if start_date and end_date:
        return start_date, end_date

    if not start_date and not end_date:
        end_date = dt.date.today()

    if periods is None:
        periods = 5000

    daycount = days_equivalent(freq, periods)

    delta = dt.timedelta(days=int(daycount * 365 / 250) + 3)

    if end_date:
        start_date = end_date - delta
    elif start_date:
        end_date = start_date + delta

    if start_date < MINDATE:
        start_date = MINDATE

    return start_date, end_date

