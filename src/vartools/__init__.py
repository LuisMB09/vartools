"""
vartools - Financial Calculations Library
==========================================

A Python library for Value at Risk (VaR), Conditional Value at Risk (CVaR),
portfolio optimization, and financial risk analytics.

Features:
    - Download stock price data from Yahoo Finance
    - Calculate VaR and CVaR for stock and forex portfolios
    - Portfolio optimization (Min Variance, Max Sharpe, Semivariance, Omega, CVaR, MCC)
    - Dynamic portfolio backtesting
    - Black-Scholes option pricing and delta hedging
    - Bond pricing and interest rate risk analytics

Usage:
    import vartools as vt

    # Download data
    data = vt.get_data(['AAPL', 'GOOGL'], '2020-01-01', '2023-01-01')

    # Calculate VaR
    var_df = vt.var_stocks(data, [100, 200], 95, True, ['AAPL', 'GOOGL'])

    # Optimize portfolio
    returns = data.pct_change().dropna()
    weights = vt.OptimizePortfolioWeights(returns, 0.04).opt_max_sharpe()

    # Bond analytics
    bond = vt.Bond(1000, 0.06, 5, 0.08)
    print(bond.summary())
"""

# Data utilities
from vartools.data import get_data

# Risk measures (VaR, CVaR)
from vartools.risk import (
    var_stocks,
    var_forex,
    var_weights,
    cvar_weights,
    cvar_contributions,
    var_apl,
)

# Portfolio utilities
from vartools.portfolio import (
    rebalance_stocks,
    plot_weights,
    simulate_portfolio,
)

# Portfolio optimization
from vartools.optimization import OptimizePortfolioWeights

# Backtesting
from vartools.backtesting import DynamicBacktesting

# Derivatives (Black-Scholes)
from vartools.derivatives import BlackScholes

# Fixed income (Bonds)
from vartools.fixed_income import Bond


__all__ = [
    # Data
    "get_data",
    # Risk
    "var_stocks",
    "var_forex",
    "var_weights",
    "cvar_weights",
    "cvar_contributions",
    "var_apl",
    # Portfolio
    "rebalance_stocks",
    "plot_weights",
    "simulate_portfolio",
    # Optimization
    "OptimizePortfolioWeights",
    # Backtesting
    "DynamicBacktesting",
    # Derivatives
    "BlackScholes",
    # Fixed Income
    "Bond",
]

__version__ = "0.1.0"
__author__ = "Luis Fernando Márquez Bañuelos"
