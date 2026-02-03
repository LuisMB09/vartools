"""Derivatives pricing and hedging (Black-Scholes model)."""

import numpy as np
import pandas as pd
from scipy.stats import norm


class BlackScholes:
    def __init__(self):
        """
        A class to implement the Black-Scholes model for option pricing and delta hedging.

        Methods:
        --------
        - call_delta(S, k, r, sigma, T): Computes the delta of a European call option.
        - put_delta(S, k, r, sigma, T): Computes the delta of a European put option.
        - delta_hedge(info_call, info_put): Computes the total delta of a portfolio of call and put options.
        """

    def _calculate_d1(self, S, k, r, sigma, T):
        """
        Compute the d1 term used in the Black-Scholes model.

        Parameters
        -----------
        S : float
            Current stock price.
        k : float
            Strike price of the option.
        r : float
            Risk-free interest rate.
        sigma : float
            Volatility of the stock.
        T : float
            Time to maturity (in years).

        Returns:
        --------
        float

            The d1 value used in the Black-Scholes formula.
        """
        return (np.log(S / k) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    # Deltas
    def call_delta(self, S, k, r, sigma, T):
        """
        Compute the delta of a European call option.

        Parameters
        -----------
        S : float
            Current stock price.
        k : float
            Strike price of the option.
        r : float
            Risk-free interest rate.
        sigma : float
            Volatility of the stock.
        T : float
            Time to maturity (in years).

        Returns:
        --------
        float

            Delta of the call option.
        """
        return norm.cdf(self._calculate_d1(S, k, r, sigma, T))

    def put_delta(self, S, k, r, sigma, T):
        """
        Compute the delta of a European put option.

        Parameters
        -----------
        S : float
            Current stock price.
        k : float
            Strike price of the option.
        r : float
            Risk-free interest rate.
        sigma : float
            Volatility of the stock.
        T : float
            Time to maturity (in years).

        Returns:
        --------
        float

            Delta of the put option.
        """
        return np.abs(norm.cdf(self._calculate_d1(S, k, r, sigma, T)) - 1)

    # Hedge
    def delta_hedge(self, info_call, info_put):
        """
        Compute the total delta of a portfolio containing multiple call and put options.

        Parameters
        -----------
        info_call : list of lists
            Each inner list contains the parameters [S, K, r, sigma, T, N] for a call option:
            - S: Current stock price
            - K: Strike price
            - r: Risk-free interest rate
            - sigma: Volatility
            - T: Time to maturity
            - N: Number of contracts

        info_put : list of lists
            Each inner list contains the parameters [S, K, r, sigma, T, N] for a put option:
            - S: Current stock price
            - K: Strike price
            - r: Risk-free interest rate
            - sigma: Volatility
            - T: Time to maturity
            - N: Number of contracts

        Returns:
        --------
        float

            The total delta of the portfolio.
        """

        # Dataframe for call and put options
        df_call = pd.DataFrame(info_call, columns=['S', 'K', 'r', 'sigma', 'T', 'N'])
        df_put = pd.DataFrame(info_put, columns=['S', 'K', 'r', 'sigma', 'T', 'N'])

        df_call['delta'] = df_call.apply(lambda row: BlackScholes().call_delta(*row[0:-1]), axis=1)
        df_put['delta'] = df_put.apply(lambda row: BlackScholes().put_delta(*row[0:-1]), axis=1)

        return np.dot(df_call['N'], df_call['delta']) - np.dot(df_put['N'], df_put['delta'])
