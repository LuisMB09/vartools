import numpy as np
import pandas as pd
pd.set_option('display.float_format', '{:,.4f}'.format)

"""
Python library for calculating VaR
The first function is for the VaR of a stock portfolio
data refers to the dataframe with the stock prices
stocks is a list with the stock tickers
n_stocks is a list with the number of stocks of each ticker
conf is the confidence level
long is a boolean that indicates if the portfolio is long or short
"""

def var_stocks(data, stocks, n_stocks, conf, long):
    data = data.sort_index()
    data = data[stocks]
    rt = data.pct_change().dropna()
    stock_value = n_stocks * data.iloc[-1]
    portfolio_value = stock_value.sum()
    w = stock_value / portfolio_value
    portfolio_return = np.dot(w, rt.T)

    if long == 1:

        var_pct = np.percentile(portfolio_return, 100-conf)
        cvar_pct = np.abs(portfolio_return[portfolio_return < var_pct].mean())

        var_cash = portfolio_value * np.abs(var_pct)
        cvar_cash = portfolio_value * cvar_pct

    else:
        
        var_pct = np.percentile(portfolio_return, conf)
        cvar_pct = portfolio_return[portfolio_return > var_pct].mean()

        var_cash = portfolio_value * var_pct
        cvar_cash = portfolio_value * cvar_pct

    var_stocks_df = pd.DataFrame({
        "Métrica": ["VaR", "cVaR"],
        "Porcentaje": [np.abs(var_pct), cvar_pct],
        "cash": [var_cash, cvar_cash]
    })

    return var_stocks_df

"""
The second function is for the VaR of a forex portfolio
data refers to the dataframe with the forex prices, be sure to download the correct currency pairs
currencies is a list with the currency pairs
positions is a list with the number of units of each currency pair
conf is the confidence level
long is a boolean that indicates if the portfolio is long or short
"""

def var_forex(data, currencies, positions, conf, long):
    data = data.sort_index()
    data = data[currencies]
    port = data * positions
    port['total'] = port.sum(axis=1)
    port['rendimiento'] = port['total'].pct_change()

    if long == 1:

        var_porcentual = np.percentile(port['rendimiento'].dropna(), 100-conf)
        var_cash = port['total'].iloc[-1] * np.abs(var_porcentual)

        cvar_porcentual = np.abs(port.query("rendimiento < @var_porcentual")['rendimiento'].mean())
        cvar_cash = port['total'].iloc[-1] * cvar_porcentual

    else:

        var_porcentual = np.percentile(port['rendimiento'].dropna(), conf)
        var_cash = port['total'].iloc[-1] * var_porcentual

        cvar_porcentual = port.query("rendimiento > @var_porcentual")['rendimiento'].mean()
        cvar_cash = port['total'].iloc[-1] * cvar_porcentual

    var_df = pd.DataFrame({
        "Métrica": ["VaR", "cVaR"],
        "Porcentual": [np.abs(var_porcentual), cvar_porcentual],
        "Cash": [var_cash, cvar_cash]
    })

    return var_df