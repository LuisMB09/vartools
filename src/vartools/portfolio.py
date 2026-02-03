"""Portfolio utilities: rebalancing, plotting, and simulation."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def rebalance_stocks(w_original: list, target_weights: list, data: pd.DataFrame, stocks: list, portfolio_value: float) -> pd.DataFrame:
    """
    Rebalance a portfolio of stocks to achieve target weights.

    Parameters
    -----------
    w_original : list
        The original weights of the portfolio.
    target_weights : list
        The target weights for the portfolio.
    data : pd.DataFrame
        A DataFrame containing historical stock prices, indexed by date.
    stocks : list
        A list of column names representing the stocks to be included in the portfolio.
    portfolio_value : float
        The total value of the portfolio.

    Returns:
    -----------
    w_df : pd.DataFrame

        A DataFrame containing the original and target weights, as well as the number of shares to buy/sell.
    """

    data = data.sort_index()
    data = data[stocks]
    n_stocks = (target_weights - w_original) * portfolio_value / data.iloc[-1]

    w_df = pd.DataFrame({
    "Original Weights": w_original,
    "Target Weights": target_weights,
    "Shares (Buy/Sell)" : n_stocks
    })

    return w_df.T


def plot_weights(stocks: list, weights: list | np.ndarray):
    """
    A function to plot the weights of a portfolio.

    Parameters
    -----------
    stocks : list
        A list of stock tickers.
    weights : list | np.ndarray
        A list of weights for the portfolio

    Returns:
    -----------
        A pie chart showing the portfolio weights.
    """

    df = pd.DataFrame(weights, index=stocks, columns=['w'])
    filtered_df = df[df['w'] > 0.000001]
    labels = filtered_df.index
    values = filtered_df.iloc[: , 0]

    plt.rcParams['figure.facecolor'] = 'lightgray'
    cmap = plt.get_cmap("Blues")
    custom_colors = cmap(np.linspace(0, 1, len(labels)))

    plt.figure(figsize=(8, 8))
    plt.pie(values, labels=labels, autopct='%1.2f%%', startangle=90, colors=custom_colors)
    plt.title("Portfolio Weights")
    plt.show()


def simulate_portfolio(data: pd.DataFrame, weights: list | np.ndarray, days: int, N: int = 10000) -> np.ndarray:
    """
    Simulate future portfolio price paths using the Cholesky decomposition method,
    preserving asset correlations.

    Parameters
    -----------
    data : pd.DataFrame
        A DataFrame containing historical asset prices, indexed by date.
        Each column represents a different asset.
    weights : list | np.ndarray
        A list of portfolio weights for each asset. Must sum to 1.
    days : int
        The number of days to simulate forward.
    N : int, optional
        The number of simulation paths. Defaults to 10000.

    Returns:
    -----------
    portfolio_simulated_returns : np.ndarray
        A 2D array of shape (days, N) containing the cumulative portfolio
        value paths, starting from 1.
    """

    returns = data.pct_change().dropna()
    mean_returns = returns.mean()
    cov_returns = returns.cov()

    portfolio_return = np.dot(weights, mean_returns)
    mean_matrix = np.full(shape=(days, len(weights)), fill_value=portfolio_return)

    L = np.linalg.cholesky(cov_returns)
    portfolio_simulated_returns = np.zeros((days, N))

    for m in range(N):
        Z = np.random.normal(size=(days, len(weights)))
        daily_returns = mean_matrix.T + L @ Z.T
        portfolio_simulated_returns[:, m] = np.cumprod(np.dot(weights, daily_returns) + 1)

    return portfolio_simulated_returns
