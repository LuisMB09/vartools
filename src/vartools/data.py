"""Data download utilities."""

import yfinance as yf


def get_data(stocks: str | list, start_date: str, end_date: str):
    """
    A function to download stock data from Yahoo Finance.

    Parameters
    -----------
    stocks : str | list
        The stock tickers to download.
    start_date : str
        The start date for the data.
    end_date : str
        The end date for the data.

    Returns:
    -----------
    data : DataFrame

        A DataFrame containing the stock data.
    """

    if isinstance(stocks, str):
        stocks = [stocks]
    data = yf.download(stocks, start=start_date, end=end_date)['Close'][stocks]
    return data
