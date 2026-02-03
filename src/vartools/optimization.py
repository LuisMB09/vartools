"""Portfolio optimization strategies."""

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from vartools._validation import _validate_confidence


class OptimizePortfolioWeights:
    """
    A class to optimize portfolio weights using various methods. The optimization strategies include:
        - Minimum Variance
        - Maximum Sharpe Ratio
        - Minimum Target Semivariance
        - Maximum Omega
        - Minimum CVaR
        - Minimum CVaR Contribution (MCC)
    """

    def __init__(self, returns: pd.DataFrame, risk_free: float):
        """
        Initialize the portfolio optimizer.

        Parameters
        -----------
        returns : pd.DataFrame
            A DataFrame containing daily asset returns, with each column representing an asset.
        risk_free : float
            The annualized risk-free rate (e.g., 0.04 for 4%).
        """

        self.rets = returns
        self.cov = returns.cov()
        self.rf = risk_free / 252
        self.n_stocks = len(returns.columns)

    # Min Variance
    def opt_min_var(self):
        """
        Compute the portfolio weights that minimize total portfolio variance.

        Returns:
        -----------
        weights : np.ndarray
            The optimized weights for the minimum variance portfolio.
        """

        def var(w): return w.T @ self.cov @ w

        w0 = np.ones(self.n_stocks)/self.n_stocks

        bounds = [(0, 1)] * self.n_stocks

        def constraint(w): return sum(w)-1

        result = minimize(fun=var, x0=w0, bounds=bounds,
                          constraints={'fun': constraint, 'type': 'eq'},
                          tol=1e-16)

        return result.x

    # Sharpe Ratio
    def opt_max_sharpe(self):
        """
        Compute the portfolio weights that maximize the Sharpe Ratio.

        Returns:
        -----------
        weights : np.ndarray
            The optimized weights for the maximum Sharpe ratio portfolio.
        """
        rets = self.rets
        rend, cov, rf = self.rets.mean(), self.cov, self.rf

        def sr(w): return -((np.dot(rend, w) - rf) /
                            ((w.reshape(-1, 1).T @ cov @ w) ** 0.5))

        result = minimize(sr, np.ones(len(rets.T)), bounds=[(0, None)] * len(rets.T),
                          constraints={'fun': lambda w: sum(
                              w) - 1, 'type': 'eq'},
                          tol=1e-16)

        return result.x

    # Semivariance method
    def opt_min_semivar(self, rets_benchmark):
        """
        Compute the portfolio weights that minimize target semivariance relative to a benchmark.

        Parameters
        -----------
        rets_benchmark : pd.DataFrame
            A DataFrame containing the daily returns of the benchmark.

        Returns:
        -----------
        weights : np.ndarray
            The optimized weights for the minimum semivariance portfolio.
        """

        rets, corr = self.rets.copy(), self.rets.corr()

        diffs = rets-rets_benchmark.values

        below_zero_target = diffs[diffs < 0].fillna(0)
        target_downside = np.array(below_zero_target.std())

        target_semivariance = np.multiply(target_downside.reshape(
            len(target_downside), 1), target_downside) * corr

        def semivar(w): return w.T @ target_semivariance @ w

        w0 = np.ones(self.n_stocks)/self.n_stocks

        bounds = [(0, 3)] * self.n_stocks

        def constraint(w): return sum(w)-1

        result = minimize(fun=semivar, x0=w0, bounds=bounds,
                          constraints={'fun': constraint, 'type': 'eq'}, tol=1e-16)

        return result.x

    # Omega
    def opt_max_omega(self, rets_benchmark):
        """
        Compute the portfolio weights that maximize the Omega ratio relative to a benchmark.

        Parameters
        -----------
        rets_benchmark : pd.DataFrame
            A DataFrame containing the daily returns of the benchmark.

        Returns:
        -----------
        weights : np.ndarray
            The optimized weights for the maximum Omega ratio portfolio.
        """

        rets = self.rets.copy()

        diffs = rets-rets_benchmark.values

        below_zero_target = diffs[diffs < 0].fillna(0)
        above_zero_target = diffs[diffs > 0].fillna(0)

        target_downside = np.array(below_zero_target.std())
        target_upside = np.array(above_zero_target.std())
        o = target_upside/target_downside

        def omega(w): return -sum(o * w)

        w0 = np.ones(self.n_stocks)/self.n_stocks

        bounds = [(0, 3)] * self.n_stocks

        def constraint(w): return sum(w)-1

        result = minimize(fun=omega, x0=w0, bounds=bounds,
                          constraints={'fun': constraint, 'type': 'eq'}, tol=1e-16)

        return result.x

    # Min CVaR
    def opt_min_cvar(self, alpha):
        """
        Compute the portfolio weights that minimize Conditional Value at Risk (CVaR).

        Parameters
        -----------
        alpha : int | float
            The confidence level for the CVaR calculation (e.g., 95 for 95% confidence).

        Returns:
        -----------
        weights : np.ndarray
            The optimized weights for the minimum CVaR portfolio.
        """

        _validate_confidence(alpha, "alpha")
        returns = self.rets.values

        def portfolio_returns(w):
            return returns @ w

        def cvar_objective(w):
            pr = portfolio_returns(w)

            # Low percentile of returns (left tail)
            var = np.percentile(pr, 100 - alpha)

            # CVaR as mean of worst returns
            return -pr[pr <= var].mean()

        w0 = np.ones(self.n_stocks) / self.n_stocks
        bounds = [(0, 1)] * self.n_stocks
        constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]

        result = minimize(
            fun=cvar_objective,
            x0=w0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            tol=1e-8
        )

        return result.x

    # MCC Portfolio
    def opt_mcc(self, alpha):
        """
        Compute the portfolio weights that minimize the maximum individual asset CVaR contribution (MCC).

        Parameters
        -----------
        alpha : int | float
            The confidence level for the CVaR calculation (e.g., 95 for 95% confidence).

        Returns:
        -----------
        weights : np.ndarray
            The optimized weights for the minimum CVaR contribution portfolio.
        """

        _validate_confidence(alpha, "alpha")
        returns = self.rets
        n_assets = self.n_stocks

        def portfolio_returns(w):
            return returns.values @ w

        def individual_cvar_contributions(w):
            pr = portfolio_returns(w)

            # Low percentile of returns (left tail)
            var = np.percentile(pr, 100 - alpha)

            bad_days = pr <= var

            # Individual CVaR contributions
            contributions = [
                -returns.iloc[bad_days, i].mean() * w[i]
                for i in range(n_assets)
            ]

            return contributions

        def objective(w):
            return np.max(individual_cvar_contributions(w))

        w0 = np.ones(n_assets) / n_assets
        bounds = [(0, 1)] * n_assets
        constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]

        result = minimize(
            fun=objective,
            x0=w0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            tol=1e-8
        )

        return result.x
