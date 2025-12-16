"""yahoo price engine for the bardata framework based on yfinance"""

import re
import yfinance

from ..utils import slice_prices


def map_frequency(freq):
    """map frequency string to yfinance interval string"""

    match = re.fullmatch(r"(\d+)(\w+)", freq)
    if match:
        count, freq = match.groups()
    else:
        count = "1"

    if freq in ("day", "daily"):
        freq = "d"
    elif freq in ("week", "weekly"):
        freq = "wk"
    elif freq in ("month", "monthly"):
        freq = "mo"
    else:
        raise ValueError(f"Invalid frequency {freq}")

    return f"{count}{freq}"


def normalize_prices(prices):
    """normalize prices dataframe"""

    prices = prices.reset_index().rename(columns=lambda c: c.replace(" ", "_").lower())
    prices = prices.rename(columns=dict(index="date"))
    prices = prices.set_index("date")

    prices.index = prices.index.tz_localize(None).normalize()

    return prices


def fetch_history(ticker, interval, *, period="max"):
    """
    fetch history

    Returns:
        prices dataframe or None if not found
    """

    prices = yfinance.Ticker(ticker).history(interval=interval, period=period)

    if prices is None or prices.empty:
        return None

    prices = normalize_prices(prices)

    return prices


def fetch_prices(
    ticker, freq="daily", *, start_date=None, end_date=None, max_bars=None
):
    """fetch prices"""

    interval = map_frequency(freq)

    prices = fetch_history(ticker, interval)

    if prices is not None:
        prices = slice_prices(
            prices, start_date=start_date, end_date=end_date, max_bars=max_bars
        )

    return prices

