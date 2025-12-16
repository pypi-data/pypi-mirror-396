"""utility routines"""

import warnings

import pandas as pd

from .freqs import pandas_freq


# FIXME `extract_datetime` method also defined elsewhere
# Used mainly by time_gaps function


def extract_datetime(prices):
    """
    Extract datetime index level as a series
    Works with either simple or multiple indexes
    Return a Series with the same index as prices
    """

    for level in range(prices.index.nlevels):
        index = prices.index.get_level_values(level)
        if isinstance(index, pd.DatetimeIndex):
            return index.to_series(index=prices.index)

    raise ValueError("No datetime index!")




def resample_prices(prices, freq):
    """resample prices"""

    freq = pandas_freq(freq)

    aggspec = dict(open="first", high="max", low="min", close="last", volume="sum")
    prices = prices.resample(freq).agg(aggspec).dropna(subset=["close"])

    return prices


def concat_prices(frames, convert_utc=True, remove_duplicates=True):
    """concatanate prices and remove duplicates"""

    if convert_utc:
        frames = [f.tz_convert("UTC") for f in frames]

    prices = pd.concat(frames)

    if remove_duplicates:
        prices = prices[~prices.index.duplicated(keep="last")]

    return prices


def price_gaps(prices: pd.DataFrame, *, max_gap=0.5, dtr_fact=4.0) -> pd.Series:
    """price gaps"""

    if not prices.index.is_monotonic_increasing:
        raise ValueError("Data is not ordered!")

    gap = prices.open / prices.close.shift(1) - 1
    dtr = prices.high / prices.low - 1

    mask = (
        (gap.abs() > max_gap)
       & (gap.abs() > dtr * dtr_fact)
    )

    result = gap[mask].rename("gap")

    return result



def remove_gaps(prices: pd.DataFrame, *, max_gap=0.5) -> pd.DataFrame:
    """remove gaps in prices"""

    gaps = price_gaps(prices, max_gap=max_gap)

    if gaps is None or gaps.empty:
        return prices

    return prices[gaps.index[-1]:].copy()



def time_gaps(prices, *, max_bars=1) -> pd.Series:
    """time gaps"""

    dates = extract_datetime(prices)
    dspan = dates.diff()

    if dspan.any():
        xspan = dspan / dspan.min()
        mask = xspan > max_bars
    else:
        mask = []

    result = dspan[mask].rename("gap")

    return result


def check_prices(prices, ticker="series", warn=True, verbose=False):
    """check prices for possible gaps in price or time"""

    if prices is None:
        return False

    result = True

    pgaps = price_gaps(prices)
    tgaps = time_gaps(prices)

    if len(pgaps):
        result = False
        if warn:
            warnings.warn(f"{ticker} has {len(pgaps)} price gaps!", stacklevel=2)
        if verbose:
            print(pgaps)

    if len(tgaps):
        result = False
        if warn:
            warnings.warn(f"{ticker} has {len(tgaps)} time gaps!", stacklevel=2)
        if verbose:
            print(tgaps)

    return result


def slice_prices(prices, start_date=None, end_date=None, max_bars=None):
    """slice prices dataframe"""

    if start_date is not None:
        prices = prices.loc[start_date:]

    if end_date is not None:
        prices = prices.loc[:end_date]

    if max_bars:
        prices = prices.tail(max_bars)

    return prices
