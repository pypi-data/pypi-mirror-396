"""date utils"""

import re
import datetime

from dateutil.tz import gettz
from dateutil.relativedelta import relativedelta


DEFAULT_CLOSING = 1700

NEW_YORK = gettz("America/New_York")


def last_busday(date=None):
    """last business day before given date, backtracks on weekends"""

    if date is None:
        date = datetime.date.today()

    weekend = max(date.weekday() - 4, 0)
    if weekend > 0:
        date -= datetime.timedelta(days=weekend)

    return date


def add_busdays(date, nbdays=0):
    """adds number of business days to given date, backtracks on weekends"""

    offset = date.weekday()  # offset to monday (backward)
    nbdays = nbdays + min(offset, 5)  # add offset back (forward)
    delta = (nbdays // 5) * 7 + (nbdays % 5) - offset
    date += datetime.timedelta(days=delta)

    return date


def last_business_close(
    asof: datetime.datetime = None,
    *,
    closing_time: int = None,
    tzinfo: str = None,
    days_back: int = 0,
):
    """last business day close for specified closing time, backtracks on weekends
    Args:
        asof: reference date as datetime.datetime (defaulted to today)
        closing_time : closing time in minutes (timezone aware or not)
        tzinfo: timezone info for closing time (when provided as naive time)
        days-back: number of business days to backtrack
    """

    if closing_time is None:
        closing_time = DEFAULT_CLOSING

    if tzinfo is None:
        tzinfo = NEW_YORK

    if isinstance(tzinfo, str):
        tzinfo = gettz(tzinfo)

    if isinstance(closing_time, int):
        hour, minute = int(closing_time / 100), (closing_time % 100)
        closing_time = datetime.time(hour=hour, minute=minute)

    if not isinstance(closing_time, datetime.time):
        raise ValueError(f"Expected an int or time, got {closing_time!r}")

    # make closing_time a naive time if
    if closing_time.tzinfo is not None:
        tzinfo = closing_time.tzinfo
        closing_time.replace(tzinfo=None)

    if asof is None:
        asof = datetime.datetime.now(tzinfo)

    if not isinstance(asof, datetime.datetime):
        raise ValueError(f"Expected a datetime value {asof}")

    if tzinfo:
        asof = asof.astimezone(tzinfo)

    # asof.time() is a naive time like closing_time
    if closing_time and asof.time() < closing_time:
        days_back += 1

    date = asof.date()

    if days_back:
        date -= datetime.timedelta(days=days_back)

    # backtrack to last business day
    weekend = max(date.weekday() - 4, 0)
    if weekend > 0:
        date -= datetime.timedelta(days=weekend)

    time = closing_time or datetime.time(0)

    result = datetime.datetime.combine(date, time, tzinfo)

    return result


def quick_timedelta(period: str) -> relativedelta:
    """relativedelta from a period pecification string like 1D, 1W, 1M, 4H, 300T etc ..."""

    if match := re.fullmatch(r"(\d+)(\w)", period):
        count, freq = int(match.group(1)), match.group(2)
    else:
        raise ValueError(f"Invalid period {period!r}")

    if freq in "D":
        kwargs = dict(days=count)
    elif freq in "W":
        kwargs = dict(weeks=count)
    elif freq == "M":
        kwargs = dict(months=count)
    elif freq == "Y":
        kwargs = dict(months=count * 12)
    elif freq == "H":
        kwargs = dict(hours=count)
    elif freq == "T":
        kwargs = dict(minutes=count)
    else:
        raise ValueError(f"Invalid period {period!r}")

    return relativedelta(**kwargs)
