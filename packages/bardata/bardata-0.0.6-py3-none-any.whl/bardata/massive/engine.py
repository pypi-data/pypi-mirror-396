# price engine

import logging
import threading
import pandas as pd

from functools import lru_cache

from massive.rest import RESTClient

from .. import model
from . import utils


MAX_BARS = 5000
MAX_LIMIT = 50000

logger = logging.getLogger(__name__)


@lru_cache
def massive_engine():
    """Massive price engine factory function"""
    return MassivePrices()


class MassivePrices(model.PriceEngine):
    """Massive price engine"""

    def __init__(self):
        super().__init__()
        self._thread_local = threading.local()

    @property
    def client(self):
        if not hasattr(self._thread_local, 'client'):
            self._thread_local.client = RESTClient()
        return self._thread_local.client


    def get_prices(self, ticker, freq="daily", start_date=None, end_date=None, max_bars=None, adjusted=True):
        """
        Get prices from Massive
        
        Returns:
            Prices dataframe or None
        """

        if max_bars is None:
            max_bars = MAX_BARS

        start_date, end_date = utils.fix_dates(start_date, end_date, freq=freq, periods=max_bars)

        multiplier, timespan = utils.map_frequency(freq)

        limit = MAX_LIMIT
        sort = 'desc'

        kwds = {'ticker': ticker,
                'multiplier': multiplier,
                'timespan': timespan,
                'from_': start_date,
                'to': end_date,
                'adjusted': adjusted,
                'sort': sort,
                'limit': limit}
        
        logger.debug("kwds %s", kwds)

        # get_aggs has no pagination. use list_aggs for pagination ! 
        aggs = list(self.client.list_aggs(**kwds))

        if not aggs:
            logger.debug("No data found for %s", ticker)
            return None

        prices = pd.DataFrame.from_records(map(vars, aggs))

        prices['datetime'] = pd.to_datetime(prices.timestamp, unit="ms", utc=True)
        prices = prices.set_index('datetime').sort_index()

        if timespan in ('day', 'week', 'month'):
            prices.index = prices.index.tz_localize(None).normalize()

        prices = prices.filter(["open", "high", "low", "close", "volume", "vwap"])

        if max_bars:
            prices = prices.tail(max_bars)

        return prices

