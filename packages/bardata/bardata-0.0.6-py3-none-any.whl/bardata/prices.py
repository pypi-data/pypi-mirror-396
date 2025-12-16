"""price data"""

import numpy as np
import pandas as pd

from functools import lru_cache

from concurrent.futures import ThreadPoolExecutor

from .model import PriceEngine
from .dates import quick_timedelta
from .freqs import pandas_freq, base_frequency

from importlib.metadata import entry_points

# MAYBE add caching (boolean) parameter ... where ?
# MAYBE add source, start_date and end_date to combine_prices ?


DEFAULT_ENDOFDAY = "tiingo"
DEFAULT_INTRADAY = "massive"

ENTRY_POINTS = "bardata_prices"


@lru_cache
def default_source(freq: str = None) -> str:
    """best source for given freq"""

    if freq:
        freq = base_frequency(freq or "day")

    if freq in ("hour", "minute"):
        return DEFAULT_INTRADAY

    return DEFAULT_ENDOFDAY


@lru_cache
def price_engine(source: str = None) -> PriceEngine:
    """price engine for source"""

    if source is None:
        source = default_source()

    entries = entry_points(group=ENTRY_POINTS, name=source)

    if not entries:
        raise ValueError(f"No price engine for {source=}")

    entry = tuple(entries)[0]

    engine = entry.load()()

    return engine


class MultiEngine(PriceEngine):
    """Price Engine"""

    priority: int = 0

    def __init__(self, sources: list):
        self.sources = sources

    def get_prices(
        self,
        ticker: str,
        freq: str = "daily",
        *,
        start_date=None,
        end_date=None,
        max_bars=None,
        adjusted=True,
    ):
        """fetch prices data"""
        kwds = dict(
            ticker=ticker,
            freq=freq,
            start_date=start_date,
            end_date=end_date,
            max_bars=max_bars,
            adjusted=adjusted,
        )

        for source in self.sources:
            engine = price_engine(source)
            prices = engine.get_prices(**kwds)
            if prices is not None:
                fields = ["open", "high", "low", "close", "volume"]
                prices = prices.filter(fields).assign(source=source)
                return prices


def get_prices(
    ticker: str,
    freq: str = "daily",
    *,
    source=None,
    start_date=None,
    end_date=None,
    max_bars=None,
    adjusted=True,
):
    """get prices from default engine"""

    if freq is None:
        freq = "daily"

    if source is None:
        source = default_source(freq=freq)

    engine = price_engine(source)

    return engine.get_prices(
        ticker,
        freq=freq,
        start_date=start_date,
        end_date=end_date,
        max_bars=max_bars,
        adjusted=adjusted,
    )


def collect_prices(
    tickers,
    *,
    freq="daily",
    source=None,
    start_date=None,
    end_date=None,
    max_bars=None,
    use_threads=True,
):
    """
    Iterate ticker, prices pairs for list of tickers

    Used mainly by combine_prices!
    """

    if source is None:
        source = default_source(freq=freq)

    kwds = dict(
        freq=freq,
        source=source,
        start_date=start_date,
        end_date=end_date,
        max_bars=max_bars,
    )

    if use_threads:
        executor = ThreadPoolExecutor()

        fvmap = {
            ticker: executor.submit(get_prices, ticker, **kwds) for ticker in tickers
        }

        for ticker, fv in fvmap.items():
            prices = fv.result()
            if prices is not None:
                yield ticker, prices
    else:
        for ticker in tickers:
            prices = get_prices(ticker, **kwds)
            if prices is not None:
                yield ticker, prices


def combine_prices(
    tickers,
    *,
    freq="daily",
    source=None,
    item="close",
    max_bars=None,
    period=None,
    resample=None,
    pct_change=False,
    log_returns=False,
    use_threads=True,
):
    """
    Matrix of closing prices for multiple tickers aligned by date

    Used mainly by multiple_regression!

    To insure better aliognement use resample instead of freq
    """

    data = {
        k: v[item]
        for k, v in collect_prices(
            tickers,
            freq=freq,
            source=source,
            max_bars=max_bars,
            use_threads=use_threads,
        )
    }

    result = pd.DataFrame(data).dropna()

    if resample is not None:
        rule = pandas_freq(resample)
        result = result.resample(rule).agg("last")

    if period:
        delta = quick_timedelta(period)
        enddate = result.index[-1]
        begdate = enddate - delta
        result = result.loc[begdate:]

    if log_returns:
        result = result.apply(np.log).diff().dropna()

    if pct_change:
        result = result.apply(np.log).diff().dropna().apply(np.exp) - 1

    return result
