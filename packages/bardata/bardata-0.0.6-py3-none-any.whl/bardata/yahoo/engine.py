"""yahoo price engine for the bardata framework based on yfinance"""

import warnings

from bardata import model

from .utils import fetch_prices


def yahoo_engine():
    return YahooPrices()


class YahooPrices(model.PriceEngine):
    """Yahoo price engine"""
    priority = 0

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
        """
        Get prices for a ticker
        
        Returns:
            prices dataframe or None
        """

        if not adjusted:
            warnings.warn(f"{__name__} supports only adjusted data")

        return fetch_prices(
            ticker,
            freq=freq,
            start_date=start_date,
            end_date=end_date,
            max_bars=max_bars,
        )
