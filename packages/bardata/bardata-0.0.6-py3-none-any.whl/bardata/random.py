"""random data"""

import numpy as np
import pandas as pd
import datetime as dt

from . import model

from .freqs import pandas_freq, split_frequency


MAXIMUM_PERIODS = dict(day=5000, week=1000, month=200, hour=20000, minute=20000)
DEFAULT_PERIODS = 5000


def maximum_periods(freq: str):
    count, freq = split_frequency(freq)
    return int(MAXIMUM_PERIODS.get(freq, 200) / count)


def date_index(periods=None, freq=None, *, start_date=None, end_date=None):
    """sample dates (wrapper around pandas date_range)"""

    if freq is None:
        freq = "daily"

    if not start_date and not end_date:
        end_date = dt.date.today()

    if start_date and end_date:
        periods = None
    elif periods is None:
        periods = DEFAULT_PERIODS

    max_periods = maximum_periods(freq)
    if periods > max_periods:
        periods = max_periods

    freq = pandas_freq(freq)

    if isinstance(start_date, str):
        start_date = pd.to_datetime(start_date)

    if isinstance(end_date, str):
        end_date = pd.to_datetime(end_date)

    dates = pd.date_range(periods=periods, start=start_date, end=end_date, freq=freq)

    if periods and len(dates) > periods:
        dates = dates[-periods:]

    return dates


def random_walk(
    periods=None,
    freq="daily",
    *,
    start_date=None,
    end_date=None,
    start_value=100.0,
    volatility=0.20,
    fwd_rate=0.10,
    name=None,
    seed=None,
):
    """random walk series"""

    generator = np.random.default_rng(seed)

    dates = date_index(
        freq=freq, periods=periods, start_date=start_date, end_date=end_date
    )
    count = len(dates)

    avgdelta = dates.diff().mean()
    sampling = pd.Timedelta(days=365) / avgdelta

    fwd = np.log(1 + fwd_rate) / sampling
    std = volatility / np.sqrt(sampling)

    change = generator.standard_normal(count - 1) * std + np.log(1 + fwd)
    price = start_value * np.exp(np.r_[0.0, change.cumsum(0)])

    series = pd.Series(price, index=dates.values, name=name).rename_axis(index="date")

    return series


def random_prices(
    periods=None,
    freq="daily",
    *,
    start_date=None,
    end_date=None,
    start_value=100.0,
    volatility=0.20,
    fwd_rate=0.10,
    skip=0,
    volume_as_int=True,
    seed=None,
):
    """random prices dataframe"""

    generator = np.random.default_rng(seed)

    dates = date_index(
        freq=freq, periods=periods, start_date=start_date, end_date=end_date
    )
    count = len(dates)

    avgdelta = dates.diff().mean()
    sampling = pd.Timedelta(days=365) / avgdelta

    fwd = np.log(1 + fwd_rate) / sampling
    std = volatility / np.sqrt(sampling)

    rnd = generator.standard_normal((count, 4)).cumsum(1) * std + fwd
    cum = np.r_[0.0, rnd[:, -1].cumsum(0)[:-1]]

    op = start_value * np.exp(rnd[:, 0] + cum)
    hi = start_value * np.exp(rnd.max(1) + cum)
    lo = start_value * np.exp(rnd.min(1) + cum)
    cl = start_value * np.exp(rnd[:, -1] + cum)

    vol = np.exp(generator.standard_normal(count) * 0.2 + 1.0) * 50000.0

    data = dict()

    data["date"] = dates.values
    data["open"] = op.round(2)
    data["high"] = hi.round(2)
    data["low"] = lo.round(2)
    data["close"] = cl.round(2)
    data["volume"] = vol.astype(int) if volume_as_int else vol.round(2)

    prices = pd.DataFrame(data).set_index("date")

    if skip > 0:
        prices.iloc[:skip] = np.nan

    if skip < 0:
        prices.iloc[skip:] = np.nan

    return prices


def random_dataset(ntickers=500, periods=5000, freq="daily"):
    """random prices dataset"""
    tickers = [f"X{i:03d}" for i in range(ntickers)]
    data = dict()
    for ticker in tickers:
        prices = random_prices(periods=periods)
        data[ticker] = prices
    return pd.concat(data, names=["ticker"])



class RandomPrices(model.PriceEngine):
    """Random Price Engine"""

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
        prices = random_prices(
            freq=freq, periods=max_bars, start_date=start_date, end_date=end_date
        )
        return prices


