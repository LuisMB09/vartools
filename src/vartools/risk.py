"""Value at Risk (VaR) and Conditional Value at Risk (CVaR) functions."""

import numpy as np
import pandas as pd

from vartools._validation import _validate_confidence


def var_stocks(data: pd.DataFrame, n_stocks: list, conf: int | float, long: bool, stocks: list) -> pd.DataFrame:
    """
    Calculate the Value at Risk (VaR) and Conditional Value at Risk (CVaR) for a portfolio of stocks.

    Parameters
    -----------
    data : pd.DataFrame
        A DataFrame containing historical stock prices, indexed by date.
    n_stocks : list
        Number of stocks per ticker.
    conf : int | float
        The confidence level for the VaR calculation (e.g., 95 for 95% confidence).
    long : bool
        Indicates the position type:
        - 1 for long positions
        - 0 for short positions
    stocks : list
        A list of column names representing the stocks to be included in the portfolio.
    Returns:
    -----------
    var_stocks_df : pd.DataFrame

        A DataFrame containing the VaR and CVaR values both as percentages and in cash terms.

    Notes: n_stocks and stocks must coincide in lenght and order.
    """

    _validate_confidence(conf)
    data = data.sort_index()
    data = data[stocks]
    rt = data.pct_change().dropna()
    stock_value = n_stocks * data.iloc[-1]
    portfolio_value = stock_value.sum()
    w = stock_value / portfolio_value
    portfolio_return = np.dot(w, rt.T)

    var_pct = np.percentile(portfolio_return, 100-conf) if long else np.percentile(portfolio_return, conf)
    cvar_pct = np.abs(portfolio_return[portfolio_return < var_pct].mean()) if long else portfolio_return[portfolio_return > var_pct].mean()

    var_cash, cvar_cash = np.abs(portfolio_value * var_pct), portfolio_value * cvar_pct

    var_stocks_df = pd.DataFrame({
        "Métrica": ["VaR", "cVaR"],
        "Porcentaje": [np.abs(var_pct), cvar_pct],
        "cash": [var_cash, cvar_cash]
    })

    return var_stocks_df


def var_forex(data: pd.DataFrame, positions: list, conf: int | float, long: bool, currencies: list) -> pd.DataFrame:
    """
    Calculate the Value at Risk (VaR) and Conditional Value at Risk (CVaR) for a portfolio of currencies.

    Parameters
    -----------
    data : pd.DataFrame
        A DataFrame containing historical exchange rates, indexed by date.
    positions : list
        A list of positions for each currency.
    conf : int | float
        The confidence level for the VaR calculation (e.g., 95 for 95% confidence).
    long : bool
        Indicates the position type:
        - 1 for long positions
        - 0 for short positions
    currencies : list
        A list of column names representing the currencies to be included in the portfolio.

    Returns:
    -----------
    var_df : pd.DataFrame

        A DataFrame containing the VaR and CVaR values both as percentages and in cash terms.

    Notes: n_stocks and stocks must coincide in lenght and order.
    """

    _validate_confidence(conf)
    data = data.sort_index()
    data = data[currencies]
    port = data * positions
    port['total'] = port.sum(axis=1)
    portfolio_return = port['total'].pct_change().dropna()

    var_porcentual = np.percentile(portfolio_return, 100-conf) if long else np.percentile(portfolio_return, conf)
    cvar_porcentual = np.abs(portfolio_return[portfolio_return < var_porcentual].mean()) if long else portfolio_return[portfolio_return > var_porcentual].mean()

    var_cash, cvar_cash = np.abs(port['total'].iloc[-1] * var_porcentual), port['total'].iloc[-1] * cvar_porcentual

    var_df = pd.DataFrame({
        "Métrica": ["VaR", "cVaR"],
        "Porcentual": [np.abs(var_porcentual), cvar_porcentual],
        "Cash": [var_cash, cvar_cash]
    })

    return var_df


def var_weights(data: pd.DataFrame, weights: list | np.ndarray, conf: int | float) -> float:
    """
    A function to calculate the Value at Risk (VaR) for a portfolio of stocks.

    Parameters
    -----------
    data : pd.DataFrame
        A DataFrame containing historical stock prices, indexed by date.
    weights : list | np.ndarray
        A list of weights for the portfolio.
    conf : int | float
        The confidence level for the VaR calculation (e.g., 95 for 95% confidence).

    Returns:
    -----------
    var : float

        The VaR value for the portfolio.
    """

    _validate_confidence(conf)
    data = data.sort_index()
    rt = data.pct_change().dropna()
    portfolio_returns = np.dot(weights, rt.T)
    return np.abs(np.percentile(portfolio_returns, 100-conf))


def cvar_weights(data: pd.DataFrame, weights: list | np.ndarray, conf: int | float) -> float:
    """
    A function to calculate the Conditional Value at Risk (CVaR) for a portfolio of stocks.

    Parameters
    -----------
    data : pd.DataFrame
        A DataFrame containing historical stock prices, indexed by date.
    weights : list | np.ndarray
        A list of weights for the portfolio.
    conf : int | float
        The confidence level for the CVaR calculation (e.g., 95 for 95% confidence).

    Returns:
    -----------
    cvar_pct : float

        The CVaR value for the portfolio.
    """

    _validate_confidence(conf)
    data = data.sort_index()
    rt = data.pct_change().dropna()
    portfolio_returns = np.dot(weights, rt.T)
    var = np.percentile(portfolio_returns, 100-conf)
    cvar_pct = np.abs(portfolio_returns[portfolio_returns < var].mean())
    return cvar_pct


def cvar_contributions(weights: list | np.ndarray, returns: pd.DataFrame, alpha: float) -> list:
    """
    A function to calculate the CVaR contributions of each asset in a portfolio.

    Parameters
    -----------
    weights : list | np.ndarray
        A list of weights for the portfolio.
    returns : pd.DataFrame
        A DataFrame containing the returns of the assets in the portfolio.
    alpha : float
        The alpha value for the CVaR calculation (e.g., 95 for 95% confidence).

    Returns:
    -----------
    contributions : list

        A list containing the CVaR contributions of each asset in the portfolio.
    """

    _validate_confidence(alpha, "alpha")
    n_assets = len(weights)

    def portfolio_return(returns, weights):
        return np.dot(returns, weights)

    def individual_cvar_contributions(weights, returns, alpha):
        portfolio_returns = portfolio_return(returns, weights)
        var = np.percentile(portfolio_returns, 100 - alpha)

        # check which days are in the cvar for the portfolio
        bad_days_portfolio = portfolio_returns < var

        contributions = []
        # check the returns of each asset the days where the portfolio is in the cvar to know the contribution
        for i in range(n_assets):
            asset_contribution = -returns.iloc[:, i][bad_days_portfolio].mean() * weights[i]
            contributions.append(asset_contribution)

        return contributions

    contributions = individual_cvar_contributions(weights, returns, alpha)

    return contributions


def var_apl(data: pd.DataFrame, posiciones: list | np.ndarray, conf: float, long: bool):
    """
    A function that calculates the Value at Risk (VaR) and Conditional Value at Risk (CVaR) adjusted by liquidity cost for a portfolio.

    Parameters
    -----------
    data : pd.DataFrame
        A DataFrame containing historical exchange rates, indexed by date.
    posiciones : list | np.ndarray
        A list of positions for each currency.
    conf : float
        The confidence level for the VaR calculation (e.g., 95 for 95% confidence).
    long : bool
        Indicates the position type:
        - 1 for long positions
        - 0 for short positions

    Returns:
    -----------
    resultados : pd.DataFrame

        A DataFrame containing the VaR and CVaR values both as percentages and in cash terms.
    """

    _validate_confidence(conf)
    data = data.sort_index()

    # Bid y Ask
    bid_columns = [col for col in data.columns if 'Bid' in col]
    ask_columns = [col for col in data.columns if 'Ask' in col]

    # Mid
    mid_columns = [f'Mid.{i}' for i in range(len(bid_columns))]
    data[mid_columns] = (data[bid_columns].values + data[ask_columns].values) / 2

    # Spreads
    spread_columns = [f'Spread.{i}' for i in range(len(bid_columns))]
    data[spread_columns] = (data[ask_columns].values - data[bid_columns].values) / data[mid_columns].values

    # Returns
    return_columns = [f'Return.{i}' for i in range(len(mid_columns))]
    data[return_columns] = data[mid_columns].pct_change()

    # Weights
    value = posiciones * data[mid_columns].iloc[-1].values
    pv = np.sum(value)
    w = value / pv

    # Portfolio return
    data['port_ret'] = np.dot(data[return_columns], w)

    # VaR calculation
    var_pct = np.percentile(data['port_ret'].dropna(), 100 - conf) if long else np.percentile(data['port_ret'].dropna(), conf)
    var_cash = pv * var_pct

    # C-VaR calculation
    cvar_pct = data['port_ret'][data['port_ret'] < var_pct].dropna().mean() if long else data['port_ret'][data['port_ret'] > var_pct].dropna().mean()
    cvar_cash = pv * cvar_pct

    # Liquidity cost
    cl_prom = data[spread_columns].mean()
    cl_estr = np.percentile(data[spread_columns], 99, axis=0)

    # VaR adjusted by liquidity cost
    var_apl_prom, var_apl_estr = np.abs(((var_pct - np.dot(w, cl_prom), var_pct - np.dot(w, cl_estr)) if long
                                else (var_pct + np.dot(w, cl_prom), var_pct + np.dot(w, cl_estr))))

    var_apl_prom_cash, var_apl_estr_cash = np.abs(((var_cash - np.dot(value, cl_prom), var_cash - np.dot(value, cl_estr)) if long
                                            else (var_cash + np.dot(value, cl_prom), var_cash + np.dot(value, cl_estr))))

    # C-VaR adjusted by liquidity cost
    cvar_apl_prom, cvar_apl_estr = np.abs(((cvar_pct - np.dot(w, cl_prom), cvar_pct - np.dot(w, cl_estr)) if long
                                    else (cvar_pct + np.dot(w, cl_prom), cvar_pct + np.dot(w, cl_estr))))

    cvar_apl_prom_cash, cvar_apl_estr_cash = np.abs(((cvar_cash - np.dot(value, cl_prom), cvar_cash - np.dot(value, cl_estr)) if long
                                            else (cvar_cash + np.dot(value, cl_prom), cvar_cash + np.dot(value, cl_estr))))

    resultados = pd.DataFrame({
        'Métrica': ['VaR', 'VaR Ajustado Promedio', 'VaR Ajustado Estresado', 'C-VaR', 'C-VaR Ajustado Promedio', 'C-VaR Ajustado Estresado'],
        'Porcentaje': [np.abs(var_pct), var_apl_prom, var_apl_estr, np.abs(cvar_pct), cvar_apl_prom, cvar_apl_estr],
        'Cash': [np.abs(var_cash), var_apl_prom_cash, var_apl_estr_cash, np.abs(cvar_cash), cvar_apl_prom_cash, cvar_apl_estr_cash]
    })

    return resultados
