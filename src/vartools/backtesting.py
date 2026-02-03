"""Dynamic backtesting for portfolio optimization strategies."""

import numpy as np
import pandas as pd

from vartools.optimization import OptimizePortfolioWeights


class DynamicBacktesting(OptimizePortfolioWeights):
    """
    A class to perform dynamic (rolling) backtesting of portfolio optimization strategies over a specified time horizon.

    This class extends OptimizePortfolioWeights and applies its optimization methods in a realistic
    backtesting framework, allowing portfolio weights to be recalculated at fixed intervals and
    portfolio value to evolve day by day.
    """

    def __init__(self, prices, prices_benchmark, capital, rf, months, alpha=95):
        """
        Initialize the dynamic backtesting simulation.

        Parameters
        -----------
        prices : pd.DataFrame
            A DataFrame containing historical asset prices, indexed by date.
        prices_benchmark : pd.DataFrame
            A DataFrame containing historical benchmark prices, indexed by date.
        capital : float
            The initial capital for the simulation.
        rf : float
            The annualized risk-free rate (e.g., 0.04 for 4%).
        months : int
            The number of months per rebalancing period.
        alpha : int | float, optional
            The confidence level for CVaR-based strategies (e.g., 95 for 95% confidence). Defaults to 95.
        """
        self.prices = prices
        self.prices_benchmark = prices_benchmark
        self.months = months
        self.capital = capital
        self.rf = rf
        self.alpha = alpha

        # Inicialización dummy del optimizador (se sobreescribe dinámicamente)
        super().__init__(returns=pd.DataFrame(), risk_free=rf)

    def optimize_weights(self, prices: pd.DataFrame, n_days: int, periods: int):
        """
        Compute optimized portfolio weights for a given rebalancing period.

        Parameters
        -----------
        prices : pd.DataFrame
            A DataFrame containing historical asset prices.
        n_days : int
            The number of trading days per rebalancing window.
        periods : int
            The current period index (0-based) to select the data slice.

        Returns:
        -----------
        tuple of np.ndarray
            A tuple containing the optimized weights for each strategy:
            (min_var, max_sharpe, min_semivar, max_omega, min_cvar, mcc).
        """

        # Extrae el subconjunto de precios actual para el periodo de optimización
        temp_data = prices.iloc[int(n_days * periods):int(n_days * (periods + 1)), :]

        #Extrae el subconjunto de precios del benchmark para el periodo de optimización
        temp_bench = self.prices_benchmark.copy().iloc[int(n_days * periods):int(n_days * (periods + 1)), :]

        # Calcula los rendimientientos del periodo de optimización
        temp_rets = temp_data.pct_change().dropna()

        rets_benchmark = temp_bench.pct_change().dropna() # Calcula los rendimientos del benchmark para el periodo de optimización

        # --- ACTUALIZACIÓN DEL ESTADO DEL OPTIMIZADOR (HERENCIA) --- #
        self.rets = temp_rets
        self.cov = temp_rets.cov()
        self.n_stocks = temp_rets.shape[1]

        w_minvar = self.opt_min_var()
        w_sharpe = self.opt_max_sharpe()
        w_semivar = self.opt_min_semivar(rets_benchmark)
        w_omega = self.opt_max_omega(rets_benchmark)
        w_min_cvar = self.opt_min_cvar(self.alpha)
        w_mcc = self.opt_mcc(self.alpha)

        # Se devuelven los pesos de los metodos de optimización
        return w_minvar, w_sharpe, w_semivar, w_omega, w_min_cvar, w_mcc

    def simulation(self):
        """
        Run a full dynamic backtesting simulation over the specified time horizon.

        Splits the data into rolling optimization and out-of-sample backtesting windows,
        rebalances the portfolio at fixed intervals, and simulates daily portfolio value
        evolution for each optimization strategy.

        Returns:
        -----------
        df : pd.DataFrame
            A DataFrame indexed by date with columns for each strategy's portfolio value
            over time: Min Variance, Sharpe, Semivariance, Omega, Min CVaR, and MCC.
        """
        n_days = round(len(self.prices) / round(len(self.prices) / 252 / (self.months / 12)), 0)

        # Es el capital inicial de la simulación/bt
        capital = self.capital

        # Se hace una copia de los precios y se extrae el subconjunto de los precios para el period de optimización
        opt_data = self.prices.copy().iloc[:int(n_days), :]

        # Se hace una copia de los precios y se extrae el subconjunto de los precios para el periodo de simulación/bt
        backtesting_data = self.prices.copy().iloc[int(n_days):, :]

        # Se calculan los rendimientos del periodo de simulación/bt
        backtesting_rets = backtesting_data.pct_change().dropna()

        # Se inicializa los contadores de los días y de los periodos
        day_counter, periods_counter = 0, 0

        # Lista para almacenar el capital a lo largo del tiempo para estrategia
        minvar, sharpe, semivar, omega, min_cvar, mcc = [capital], [capital], [capital], [capital], [capital], [capital]

        # Se obtienne los pesos optimizados
        w_minvar, w_sharpe, w_semivar, w_omega, w_min_cvar, w_mcc = self.optimize_weights(opt_data, n_days, 0)

        # Se itera dia a dia para
        for day in range(len(backtesting_data) - 1):

            # Si el contador de dias es menor al numero de didas de optmización , hace:
            if day_counter < n_days:

                sharpe.append(sharpe[-1] * (1 + sum(backtesting_rets.iloc[day, :] * w_sharpe)))
                minvar.append(minvar[-1] * (1 + sum(backtesting_rets.iloc[day, :] * w_minvar)))
                semivar.append(semivar[-1] * (1 + sum(backtesting_rets.iloc[day, :] * w_semivar)))
                omega.append(omega[-1] * (1 + sum(backtesting_rets.iloc[day, :] * w_omega)))
                min_cvar.append(min_cvar[-1] * (1 + sum(backtesting_rets.iloc[day, :] * w_min_cvar)))
                mcc.append(mcc[-1] * (1 + sum(backtesting_rets.iloc[day, :] * w_mcc)))
            else:

                w_minvar, w_sharpe, w_semivar, w_omega, w_min_cvar, w_mcc = self.optimize_weights(backtesting_data, n_days, periods_counter)

                sharpe.append(sharpe[-1] * (1 + sum(backtesting_rets.iloc[day, :] * w_sharpe)))
                minvar.append(minvar[-1] * (1 + sum(backtesting_rets.iloc[day, :] * w_minvar)))
                semivar.append(semivar[-1] * (1 + sum(backtesting_rets.iloc[day, :] * w_semivar)))
                omega.append(omega[-1] * (1 + sum(backtesting_rets.iloc[day, :] * w_omega)))
                min_cvar.append(min_cvar[-1] * (1 + sum(backtesting_rets.iloc[day, :] * w_min_cvar)))
                mcc.append(mcc[-1] * (1 + sum(backtesting_rets.iloc[day, :] * w_mcc)))
                periods_counter += 1
                day_counter = 0

            day_counter += 1

        # Crear DataFrame con los resultados de la simulación/bt
        df = pd.DataFrame()
        df['Date'] = backtesting_data.index
        df['Date'] = pd.to_datetime(df['Date'])
        df['Min Variance'] = minvar
        df['Sharpe'] = sharpe
        df['Semivariance'] = semivar
        df['Omega'] = omega
        df['Min CVaR'] = min_cvar
        df['MCC'] = mcc
        df.set_index('Date', inplace=True)

        return df
