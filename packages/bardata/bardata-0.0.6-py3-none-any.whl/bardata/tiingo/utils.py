"""Utility methods"""

import re


def map_ticker(ticker: str):
    """Map ticker to vendor ticker"""
    return ticker.replace(".", "-")


def map_frequency(freq):
    """Map frequency to vendor code"""

    freq = dict(hourly="1hour", minute="1min").get(freq, freq)

    if re.fullmatch(r"daily|weekly|monthly", freq):
        return freq

    if re.fullmatch(r"(\d+)hour", freq):
        return freq

    if re.fullmatch(r"(\d+)min", freq):
        return freq

    raise ValueError("Invalid freq %r" % freq)


def adjust_prices(prices):
    """Adjust prices"""
    if "adjClose" in prices.columns:
        prices = prices.filter(["adjOpen", "adjHigh", "adjLow", "adjClose", "adjVolume"])
        prices = prices.rename(columns=lambda n: n.removeprefix("adj").lower())
    return prices

