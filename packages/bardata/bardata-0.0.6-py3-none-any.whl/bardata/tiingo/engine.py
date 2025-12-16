"""Price Engine"""

import logging
import datetime as dt

from functools import lru_cache, cached_property

from tiingo import TiingoClient
from tiingo.restclient import RestClientError

from .. import model
from . import utils


# MAXBARS = 10000

logger = logging.getLogger(__name__)


@lru_cache
def tiingo_engine():
    return TiingoPrices()


class TiingoPrices(model.PriceEngine):
    """Tiingo price engine"""

    @cached_property
    def client(self):
        config = dict(session=True)
        return TiingoClient(config)

    def ignore_error(self, error):
        """Ignore 404 errors"""

        if isinstance(error, RestClientError):
            error = error.args[0]

        if hasattr(error, "response"):
            response = error.response
        else:
            return False

        if response.status_code == 404:
            return True
        
        return False


    def get_prices(self, ticker, freq="daily", start_date=None, end_date=None, max_bars=None, adjusted=True):
        """Get prices dataframe"""

        ticker = utils.map_ticker(ticker)
        frequency = utils.map_frequency(freq)

        if end_date is None:
            end_date = dt.date.today()

        kwds = {
            'tickers': ticker,
            'startDate': start_date,
            'endDate': end_date,
            'frequency': frequency
        }

        try:
            prices = self.client.get_dataframe(**kwds)
        except Exception as ex:
            if self.ignore_error(ex):
                return None
            else:
                raise

        if adjusted:
            prices = utils.adjust_prices(prices)

        if freq in ("daily", "weekly", "monthly"):
            prices.index = prices.index.tz_localize(None).normalize()

        prices = prices.filter(["open", "high", "low", "close", "volume"])

        if max_bars:
            prices = prices.tail(max_bars)

        return prices
