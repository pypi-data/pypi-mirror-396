""" Trading scanner """

import logging
import warnings

import pandas as pd

from dataclasses import dataclass

from datetime import datetime

from concurrent.futures import ThreadPoolExecutor, as_completed

from .model import PriceEngine
from .errors import DataNotFoundError
from .prices import price_engine
from .utils import price_gaps, remove_gaps


logger = logging.getLogger(__name__)

DEFAULT_MAX_BARS = 5000


@dataclass
class Scanner:
    """
    Class to fetch a list of tickers into a dataset

    Attributes:
        tickers: list of tickers
        freq: frequency
        start_date: timeframe
        end_date: timeframe
        max_bars: max number of bars (default 5000)
    """

    tickers: list = None
    freq: str = "daily"
    source: str = None

    start_date: datetime = None
    end_date: datetime = None
    max_bars: int = DEFAULT_MAX_BARS
    remove_gaps: bool = False
    
    engine: PriceEngine = None

    def __post_init__(self):
        if self.engine and self.source:
            raise ValueError("Specify either source or engine")

        if self.engine is None:
            self.engine = price_engine(self.source)

    @staticmethod
    def get_executor(max_workers=None):
        """create executor or returns none when max_workers == 0 !"""

        if max_workers == 0:
            return None

        return ThreadPoolExecutor(max_workers=max_workers)


    def fetch_prices(self, ticker):
        """fetches prices via finance.get_prices"""

        prices = self.engine.get_prices(
            ticker,
            freq=self.freq,
            start_date=self.start_date,
            end_date=self.end_date,
            max_bars=self.max_bars,
        )

        if self.remove_gaps:
            gaps = price_gaps(prices)
            if len(gaps):
                warnings.warn(f"{ticker} has {len(gaps)} price gaps!", stacklevel=2)
                prices = remove_gaps(prices)

        return prices


    @staticmethod
    def convert_result(result, *, ticker):
        """convert result to (ticker, result) or None"""

        if result is None or len(result) == 0:
            return None

        if isinstance(result, pd.DataFrame):
            return (ticker, result)

        raise ValueError("Unexpeted result type %s" % type(result).__name__)


    @staticmethod
    def concat_results(results):
        """concatente results"""
        data = dict(res for res in results if res is not None)

        result = pd.concat(data, names=["ticker"])

        return result


    def process_ticker(self, ticker, study=None):
        """handler to process ticker within executor context"""

        ignore_errors = (DataNotFoundError,)

        try:
            prices = self.fetch_prices(ticker)

            if prices is None:
                logger.warning("Ticker %s has no data!" % ticker)
                return None

            if study is not None:
                result = study(prices)
            else:
                result = prices

            return self.convert_result(result, ticker=ticker)

        except ignore_errors:
            logger.warning("Ticker %s has no data!" % ticker)

        except Exception:
            warnings.warn("Error processing %s" % ticker, stacklevel=2)
            #raise RuntimeError("Error processing %s" % ticker)



    def run(
        self, study=None, executor=None, max_workers=None 
    ):
        """runs scanner"""

        if executor is None:
            executor = self.get_executor(max_workers=max_workers)

        kwds = dict(study=study)

        if executor:
            fvs = (executor.submit(self.process_ticker, ticker, **kwds) for ticker in self.tickers)
            results = [fv.result() for fv in as_completed(fvs)]
        else:
            results = [self.process_ticker(ticker, **kwds) for ticker in self.tickers]

        logger.debug("Processing Done!")

        results = self.concat_results(results)

        return results

