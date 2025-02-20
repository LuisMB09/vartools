import numpy as np
import pandas as pd
import yfinance as yf
from scipy.stats import norm
import matplotlib.pyplot as plt
from scipy.optimize import minimize
pd.set_option('display.float_format', '{:,.4f}'.format)


def var_stocks(data, n_stocks, conf, long, stocks):
    """
    Python library for calculating VaR
    The first function is for the VaR of a stock portfolio
    data refers to the dataframe with the stock prices
    stocks is a list with the stock tickers
    n_stocks is a list with the number of stocks of each ticker
    conf is the confidence level
    long is a boolean that indicates if the portfolio is long or short
    """
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



def var_forex(data, positions, conf, long, currencies):
    """
    The second function is for the VaR of a forex portfolio
    data refers to the dataframe with the forex prices, be sure to download the correct currency pairs
    currencies is a list with the currency pairs
    positions is a list with the number of units of each currency pair
    conf is the confidence level
    long is a boolean that indicates if the portfolio is long or short
    """
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



def rebalance_stocks(w_original, target_weights, data, stocks, portfolio_value):
    """
    The third function is for the rebalancing a portfolio
    You need to calculate the value of your portfolio
    Calculate the weights of each asset
    Calculate the target weights
    data is a dataframe with the stock prices
    w_original and target_weights are vectors with the weights of each asset
    """
    data = data.sort_index()
    data = data[stocks]
    w_df = pd.DataFrame({
    "Peso Original": w_original,
    "Peso Óptimo": target_weights,
    "Acciones (C/V)" : np.floor((target_weights-w_original) * portfolio_value / data.iloc[-1])
    })
    return w_df.T



def get_data(stocks, start_date, end_date, type='Adj Close'):
    """
    The fourth function is for obtaining the stock price
    It is done in a way that the order of the columns is the same as the order of the stocks
    """
    data=yf.download(stocks, start=start_date, end=end_date)[type][stocks]
    return data



def var_weights(data, weights, conf):
    """
    The fifth function is for obtainig the VaR as a percent when you only have the weights of the portfolio
    It just receives a dataframe with the prices of the stocks (data)
    It works only for long postitons
    """
    data = data.sort_index()
    rt = data.pct_change().dropna()
    portfolio_returns = np.dot(weights, rt.T)
    var = np.percentile(portfolio_returns, 100-conf)
    cvar_pct = np.abs(portfolio_returns[portfolio_returns < var].mean())
    return np.abs(var)


def cvar_weights(data, weights, conf):
    """
    The fifth function is for obtainig the CVaR as a percent when you only have the weights of the portfolio
    It just receives a dataframe with the prices of the stocks (data)
    It works only for long postitons
    """
    data = data.sort_index()
    rt = data.pct_change().dropna()
    portfolio_returns = np.dot(weights, rt.T)
    var = np.percentile(portfolio_returns, 100-conf)
    cvar_pct = np.abs(portfolio_returns[portfolio_returns < var].mean())
    return cvar_pct



def opt_sharpe(returns, rf):
    """
    The sixth function is for obtaining the optimal weights of a portfolio to maximize the Sharpe Ratio
    It receives a dataframe with the returns of the stocks (returns) and the risk-free rate (rf)
    """
    mu = (returns.mean() * 252).values
    sigma = returns.cov().values
    n_assets = len(mu)

    # Función para minimizar (-Sharpe Ratio)
    def neg_sharpe_ratio(w, mu, sigma, rf):
        port_return = np.dot(w, mu)
        port_vol = np.sqrt(np.dot(w.T, np.dot(sigma, w))) * np.sqrt(252)
        sharpe_ratio = (port_return - rf) / port_vol
        return -sharpe_ratio
    
    # Restricciones: Suma de pesos = 1
    constraints = ({
        'type': 'eq',
        'fun': lambda w: np.sum(w) - 1
    })

    # Límites: Pesos entre 0 y 1 (no posiciones cortas)
    bounds = tuple((0, 1) for _ in range(n_assets))

    # Pesos iniciales (distribuidos uniformemente)
    w0 = np.array([1 / n_assets] * n_assets)

    # Optimización
    result = minimize(neg_sharpe_ratio, 
            w0, 
            args=(mu, sigma, rf), 
            method='SLSQP', 
            bounds=bounds, 
            constraints=constraints)
    
    # Resultados
    w_opt_sharpe = result.x

    return w_opt_sharpe



def min_variance(returns):
    """
    The seventh function is for obtaining the optimal weights of a portfolio to minimize the variance
    It receives a dataframe with the returns of the stocks (returns) and the risk-free rate (rf)
    """
    mu = (returns.mean() * 252).values
    sigma = returns.cov().values
    n_assets = len(mu)

    # Función para minimizar (-Sharpe Ratio)
    def min_var(w, mu, sigma):
        port_return = np.dot(w, mu)
        port_vol = np.sqrt(np.dot(w.T, np.dot(sigma, w))) * np.sqrt(252)
        return port_vol
    
    # Restricciones: Suma de pesos = 1
    constraints = ({
        'type': 'eq',
        'fun': lambda w: np.sum(w) - 1
    })

    # Límites: Pesos entre 0 y 1 (no posiciones cortas)
    bounds = tuple((0, 1) for _ in range(n_assets))

    # Pesos iniciales (distribuidos uniformemente)
    w0 = np.array([1 / n_assets] * n_assets)

    # Optimización
    result = minimize(min_var, 
            w0, 
            args=(mu, sigma), 
            method='SLSQP', 
            bounds=bounds, 
            constraints=constraints)
    
    # Resultados
    min_var_weights = result.x

    return min_var_weights


def min_cvar(returns, alpha):

    n_assets = len(returns.columns)

    def portfolio_return(returns, weights):
        return np.dot(returns, weights)

    # Better way to calculate CVaR than the one used in my homework 1. I used .query in the homework, but checking with friends this way is better.
    def cvar(portfolio_returns, alpha):
        var = np.percentile(portfolio_returns, alpha*100)
        cvar = -portfolio_returns[portfolio_returns < var].mean()
        return cvar

    def min_cvar(weights, returns, alpha):
        portfolio_returns = portfolio_return(returns, weights)
        return cvar(portfolio_returns, alpha)

    constraints = [
        {"type": "eq", "fun": lambda w: np.sum(w) - 1},
    ]
    bounds = tuple((0, 1) for _ in range(n_assets))

    # Initial guess
    initial_weights = np.ones(n_assets) / n_assets

    result_min_cvar = minimize(
        fun=min_cvar,
        x0=initial_weights,
        args=(returns, alpha),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        tol=1e-8
    )
    min_cvar_weights = result_min_cvar.x

    return min_cvar_weights


def mcc_portfolio(returns, alpha):
    """
    Optimizes portfolio weights using the Minimum CVaR Contribution (MCC) approach.

    Parameters:
    - returns (pd.DataFrame): DataFrame containing historical asset returns.
    - alpha (float): Significance level for CVaR (default: 0.05 for 95% confidence level).
    """

    n_assets = len(returns.columns)

    def portfolio_return(returns, weights):
        return np.dot(returns, weights)

    def cvar(portfolio_returns, alpha):
        var = np.percentile(portfolio_returns, alpha * 100)
        return -portfolio_returns[portfolio_returns < var].mean()

    def individual_cvar_contributions(weights, returns, alpha):
        portfolio_returns = portfolio_return(returns, weights)
        var = np.percentile(portfolio_returns, alpha * 100)

        bad_days_portfolio = portfolio_returns < var
        contributions = [-returns.iloc[:, i][bad_days_portfolio].mean() * weights[i] for i in range(n_assets)]
        
        return contributions

    def optimal_mcc(weights, returns, alpha):
        return np.max(individual_cvar_contributions(weights, returns, alpha))

    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
    bounds = tuple((0, 1) for _ in range(n_assets))
    initial_weights = np.ones(n_assets) / n_assets

    result = minimize(
        fun=optimal_mcc,
        x0=initial_weights,
        args=(returns, alpha),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        tol=1e-8
    )
    mcc_weights = result.x

    return mcc_weights


def cvar_contributions(weights, returns, alpha):
    """
    Calculates the individual CVaR contributions of each asset in the portfolio.
    """
    n_assets = len(weights)
    # CVaR for only long positions
    def portfolio_return(returns, weights):
        return np.dot(returns, weights)

    # Better way to calculate CVaR than the one used in my homework 1. I used .query in the homework, but checking with friends this way is better.
    def cvar(portfolio_returns, alpha):
        var = np.percentile(portfolio_returns, alpha*100)
        cvar = -portfolio_returns[portfolio_returns < var].mean()
        return cvar

    def individual_cvar_contributions(weights, returns, alpha):
        portfolio_returns = portfolio_return(returns, weights)
        var = np.percentile(portfolio_returns, alpha*100)

        # check which days are in the cvar for the portfolio
        bad_days_portfolio = portfolio_returns < var

        contributions = []
        # chech the returns of each asset the days where the portfolio is in the cvar to know the contribution
        for i in range(n_assets):
            asset_contribution = -returns.iloc[:, i][bad_days_portfolio].mean() * weights[i]
            contributions.append(asset_contribution)
        
        portfolio_cvar = cvar(portfolio_returns, alpha)

        percentage_contributions = []
        for j in range(len(contributions)):
            pct_contributions = contributions[j] / portfolio_cvar
            percentage_contributions.append(pct_contributions)
        
        return contributions
    contributions = individual_cvar_contributions(weights, returns, alpha)
    
    return contributions


def plot_weights(stocks, weights):
    """
    It creates a pie chart with the weights of the portfolio
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

class BlackScholes:
    def __init__(self, S, k, r, sigma, T):
        """
        Initialize the Black-Scholes model parameters.
        :param S: Current stock price
        :param k: Strike price
        :param r: Risk-free rate
        :param sigma: Volatility of the asset
        :param T: Time to expiration (in years)
        """
        self.S = S
        self.k = k
        self.r = r
        self.sigma = sigma
        self.T = T
        self.d1 = self._calculate_d1()

    def _calculate_d1(self):
        """
        Compute the d1 term in the Black-Scholes formula.
        """
        return (np.log(self.S / self.k) + (self.r + 0.5 * self.sigma ** 2) * self.T) / (self.sigma * np.sqrt(self.T))

    # Deltas
    def call_delta(self):
        return norm.cdf(self.d1)

    def put_delta(self):
        return np.abs(norm.cdf(self.d1) - 1)

    # Hedge
    def delta_hedge(self, info_call, info_put):

        # Dataframe for call and put options
        df_call = pd.DataFrame(info_call, columns=['S', 'K', 'r', 'sigma', 'T', 'N'])
        df_put = pd.DataFrame(info_put, columns=['S', 'K', 'r', 'sigma', 'T', 'N'])

        df_call['delta'] = df_call.apply(lambda row: BlackScholes(*row[0:-1]).call_delta(), axis=1)
        df_put['delta'] = df_put.apply(lambda row: BlackScholes(*row[0:-1]).put_delta(), axis=1)
            
        return np.dot(df_call['N'], df_call['delta']) - np.dot(df_put['N'], df_put['delta'])