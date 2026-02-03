# Financial Calculations Library

## Overview
This Python library provides functions to calculate the **Value at Risk (VaR)** and **Conditional Value at Risk (cVaR)** for financial portfolios, including stock and forex portfolios. These risk measures help in understanding potential losses under given confidence levels. It also allows you to conveniently download price data from Yahoo Finance and perform portfolio optimization using multiple strategies.

## Features
- Download stock price data.
- Calculate **VaR** and **cVaR** for a **stock portfolio**.
- Calculate **VaR** and **cVaR** for a **forex portfolio**.
- Supports both **long** and **short** positions.
- Outputs results in both **percentage** and **cash value**.
- Rebalance a **stock portfolio**.
- Portfolio optimization for multiple strategies.
- Dynamic portfolio backtest.
- **Bond pricing** and interest rate risk analytics (duration, convexity).

## Installation
Ensure you have the required dependencies installed:

```bash
pip install scipy
pip install numpy 
pip install pandas
pip install yfinance
pip install matplotlib
```

Then

```bash
pip install vartools
```
Also run

```bash
pip install --upgrade vartools
```

To get the latest version.

## Functions

### `get_data(stocks, start_date, end_date)`

A function to download stock data from Yahoo Finance.

#### Parameters:
-----------
- **stocks** : `str | list`

    The stock tickers to download.
- **start_date** : `str`

    The start date for the data in the format `YYYY-MM-DD`.
- **end_date** : `str`

    The end date for the data in the format `YYYY-MM-DD`.

#### Returns:
--------
**data** : `pd.DataFrame`

A DataFrame containing the stock data.

**Note:** If you prefer to directly download the data from yfinance it is encouraged a format like this:

```python
stocks = ["AAPL", "TSLA", "AMD", "LMT", "JPM"]
data=yf.download(stocks, start="2020-01-01", end="2023-01-01")['Close'][stocks]
```

Also if you get the data from an excel or csv file create the list `stocks` or `currencies`with the name of the columns in your file for correct functioning. Also make sure to establish yor `Date`column as index.

--------


### `var_stocks(data, n_stocks, conf, long, stocks)`

Calculate the Value at Risk (VaR) and Conditional Value at Risk (CVaR) for a portfolio of stocks.

#### Parameters:
-----------
- **data** : `pd.DataFrame`

    A DataFrame containing historical stock prices, indexed by date.
- **n_stocks** : `list`

    Number of stocks per ticker.
- **conf** : `int | float`

    The confidence level for the VaR calculation (e.g., 95 for 95% confidence).
- **long** : `bool`

    Indicates the position type:
    - 1 (True) for long positions
    - 0 (False) for short positions

- **stocks** : `list`

A list of column names representing the stocks to be included in the portfolio.

#### Returns:
--------
**var_stocks_df** : `pd.DataFrame`

A DataFrame containing the VaR and CVaR values both as percentages and in cash terms.

**Note:** Utilize this function when you have the number of shares of each stock instead of the weights, also `n_stocks` and `stocks` must coincide in lenght and order.

--------


### `var_forex(data, positions, conf, long, currencies)`

Calculate the Value at Risk (VaR) and Conditional Value at Risk (CVaR) for a portfolio of currencies.

#### Parameters:
-----------
- **data** : `pd.DataFrame`

    A DataFrame containing historical exchange rates, indexed by date.
- **positions** : `list`

    A list of positions for each currency.
- **conf** : `int | float`

    The confidence level for the VaR calculation (e.g., 95 for 95% confidence).
- **long** : `bool`

    Indicates the position type:
    - 1 (True) for long positions
    - 0 (False) for short positions

- **currencies** : `list`

    A list of column names representing the currencies to be included in the portfolio.

#### Returns:
--------
**var_df** : `pd.DataFrame`

A DataFrame containing the VaR and CVaR values both as percentages and in cash terms.

**Note:** n_stocks and stocks must coincide in lenght and order.

--------


### `rebalance_stocks(w_original, target_weights, data, stocks, portfolio_value)`

Rebalance a portfolio of stocks to achieve target weights.

#### Parameters:
-----------
- **w_original** : `list`

    The original weights of the portfolio.
- **target_weights** : `list`

    The target weights for the portfolio.
- **data** : `pd.DataFrame`

    A DataFrame containing historical stock prices, indexed by date.
- **stocks** : `list`

    A list of column names representing the stocks to be included in the portfolio.
- **portfolio_value** : `float`

    The total value of the portfolio.

#### Returns:
--------
**w_df** : `pd.DataFrame`

A DataFrame containing the original and target weights, as well as the number of shares to buy/sell.

--------


### `var_weights(data, weights, conf)`

A function to calculate the Value at Risk (VaR) for a portfolio of stocks.

#### Parameters:
-----------
- **data** : `pd.DataFrame`

    A DataFrame containing historical stock prices, indexed by date.
- **weights** : `list | np.ndarray`

    A list of weights for the portfolio.
- **conf** : `int | float`

    The confidence level for the VaR calculation (e.g., 95 for 95% confidence).

#### Returns:
--------
**var** : `float`

The VaR value for the portfolio.

**Note:** It only works for long positions, and the weights must add up to 1.

--------


### `cvar_weights(data, weights, conf)`

A function to calculate the Conditional Value at Risk (CVaR) for a portfolio of stocks.

#### Parameters:
-----------
- **data** : `pd.DataFrame`

    A DataFrame containing historical stock prices, indexed by date.
- **weights** : `list | np.ndarray`

    A list of weights for the portfolio.
- **conf** : `int | float`

    The confidence level for the CVaR calculation (e.g., 95 for 95% confidence).

#### Returns:
--------
**cvar_pct** : `float`

The CVaR value for the portfolio.

**Note:** It only works for long positions, and the weights must add up to 1.

--------


### `def cvar_contributions(weights, returns, alpha)`

A function to calculate the CVaR contributions of each asset in a portfolio.

#### Parameters:
-----------
- **weights** : `list | np.ndarray`

    A list of weights for the portfolio.
- **returns** : `pd.DataFrame`

    A DataFrame containing the returns of the assets in the portfolio.
- **alpha** : `float`

    The confidence level for the CVaR calculation (e.g., 95 for 95% confidence).

#### Returns:
--------
**contributions** : `list`

**Note:** This portfolio strategy only works for long positions, so the weights must add up to 1.

--------


### `plot_weights(stocks, weights)`

A function to plot the weights of a portfolio.

#### Parameters:
-----------
- **stocks** : `list`

    A list of stock tickers.
- **weights** : `list | np.ndarray`

    A list of weights for the portfolio

#### Returns:
--------
A pie chart showing the portfolio weights.

--------


### `BlackScholes`

A class to implement the Black-Scholes model for option pricing and delta hedging.

#### Methods:
--------
- call_delta(S, k, r, sigma, T): Computes the delta of a European call option.
- put_delta(S, k, r, sigma, T): Computes the delta of a European put option.
- delta_hedge(info_call, info_put): Computes the total delta of a portfolio of call and put options.

-----


### `Bond`

A class to model fixed-coupon bonds with pricing and interest rate risk analytics.

This class models a standard fixed-rate bond and provides methods to calculate its theoretical price and key risk measures (duration, convexity).

#### Constructor Parameters:
-----------
- **face_value** : `float`

    Par/principal value repaid at maturity (e.g., 1000).
- **coupon_rate** : `float`

    Annual coupon rate as decimal (e.g., 0.05 for 5%).
- **years_to_maturity** : `int`

    Number of years until bond matures.
- **yield_to_maturity** : `float`

    Market discount rate as decimal.
- **payments_per_year** : `int`

    Coupon payment frequency (1=annual, 2=semi-annual, 4=quarterly, 12=monthly). Default is 1.

#### Methods:
--------
- **price()**: Calculates the bond's theoretical price as the present value of all future cash flows discounted at the yield to maturity.

- **macaulay_duration()**: Calculates the weighted average time to receive the bond's cash flows (in years).

- **modified_duration()**: Measures the percentage change in bond price for a 1% change in yield. Adjusts Macaulay Duration for compounding.

- **convexity()**: Measures the curvature of the price-yield relationship, capturing second-order effects that duration misses.

- **price_change_estimate(yield_change)**: Estimates percentage price change using duration and convexity for a given yield change (Taylor series approximation).

- **summary()**: Generates a formatted summary of all bond analytics including terms, valuation, risk metrics, and sensitivity analysis.

-----


### `OptimizePortfolioWeights`

A class to optimize portfolio asset weights using multiple quantitative portfolio construction techniques based on risk, return, and downside risk measures.

The class supports classical mean–variance optimization as well as downside-risk and tail-risk–based methods commonly used in quantitative finance.

#### Methods:

---

* **opt_min_var()**
  Computes the portfolio weights that minimize total portfolio variance subject to full investment and minimum weight constraints.

* **opt_max_sharpe()**
  Computes the portfolio weights that maximize the Sharpe Ratio using expected returns, the covariance matrix, and a risk-free rate.

* **opt_min_semivar(rets_benchmark)**
  Computes portfolio weights that minimize target semivariance relative to a benchmark return series, focusing on downside deviations only.

* **opt_max_omega(rets_benchmark)**
  Computes portfolio weights that maximize the Omega ratio by balancing upside variability against downside variability relative to a benchmark.

* **opt_min_cvar(alpha)**
  Computes portfolio weights that minimize Conditional Value at Risk (CVaR) at a specified confidence level using historical return simulations.

* **opt_mcc(alpha)**
  Computes portfolio weights that minimize the maximum individual asset contribution to portfolio CVaR (Minimum CVaR Contribution), promoting tail-risk diversification.

-----


### `DynamicBacktesting`

A class to perform dynamic (rolling) backtesting of portfolio optimization strategies over time, using periodic re-optimization of portfolio weights based on historical price data.

This class extends `OptimizePortfolioWeights` and applies its optimization methods in a realistic backtesting framework, allowing portfolio weights to be recalculated at fixed intervals and portfolio value to evolve day by day.

#### Methods:

---

* **optimize_weights(prices, n_days, periods)**
  Computes optimized portfolio weights for a given rebalancing period using historical price data.
  The method dynamically updates the inherited optimizer state and returns weights for multiple optimization strategies, including minimum variance, maximum Sharpe ratio, semivariance, Omega, minimum CVaR, and minimum CVaR contribution.

* **simulation()**
  Runs a full dynamic backtesting simulation over the specified time horizon.
  The method:

  * Splits the data into rolling optimization and out-of-sample backtesting windows
  * Rebalances the portfolio at fixed intervals
  * Simulates daily portfolio value evolution for each optimization strategy
  * Returns a time series of portfolio values for all strategies in a single DataFrame

-----

**Note:** See usage examples for better understanding.


## Usage Example
```python
import numpy as np
import pandas as pd
import yfinance as yf
import vartools as vt
import matplotlib.pyplot as plt
from scipy.optimize import minimize
```

## get_data
```python
stocks = ["AAPL", "TSLA", "AMD", "LMT", "JPM"]
start_date = "2020-01-01"
end_date = "2023-01-01"

data = vt.get_data(stocks, start_date, end_date)
```

## var_stocks
```python
stocks = ["AAPL", "TSLA", "AMD", "LMT", "JPM"]
start_date = "2020-01-01"
end_date = "2023-01-01"

data = vt.get_data(stocks, start_date, end_date)
n_stocks =[2193, 1211, 3221, 761, 1231]
conf = 95
long = True

var_df = vt.var_stocks(data, n_stocks, conf, long, stocks)
var_df
```

## var_forex
```python
currencies = ['CHFMXN=X', 'MXN=X']
start_date = "2020-01-01"
end_date = "2024-12-02"

data = vt.get_data(currencies, start_date, end_date)
positions = [7100000, 5300000] # How much you have in each currency. Must match the order in currencies.
conf = 99 # Nivel de confianza
long = True

var_forex_df = vt.var_forex(data, positions, conf, long, currencies)
var_forex_df
```

## rebalance_stocks
```python
stocks = ["AAPL", "TSLA", "AMD", "LMT", "JPM"]
start_date = "2020-01-01"
end_date = "2023-01-01"

data = vt.get_data(stocks, start_date, end_date)

rt = data.pct_change().dropna()
stock_value = n_stocks * data.iloc[-1]
portfolio_value = stock_value.sum()
w_original = stock_value / portfolio_value
w_opt = [0.33, 0.15, 0.06, 0.46, 0.00]

rebalance_df = vt.rebalance_stocks(w_original, w_opt, data, stocks, portfolio_value)
rebalance_df
```

## var_weights
```python
stocks = ["AAPL", "TSLA", "AMD", "LMT", "JPM"]
start_date = "2020-01-01"
end_date = "2023-01-01"

data = vt.get_data(stocks, start_date, end_date)

weights = [0.2457, 0.1301, 0.1820, 0.3064, 0.1358]
conf = 95
var_pct = vt.var_weights(data, weights, conf)
var_pct
```

## cvar_weights
```python
stocks = ["AAPL", "TSLA", "AMD", "LMT", "JPM"]
start_date = "2020-01-01"
end_date = "2023-01-01"

data = vt.get_data(stocks, start_date, end_date)

weights = [0.2457, 0.1301, 0.1820, 0.3064, 0.1358]
conf = 95
cvar_pct = vt.cvar_weights(data, weights, conf)
cvar_pct
```


## cvar_contributions
```python
# bonds, commodities, equities and real estate
stocks = ['VBTLX', 'GSG', 'VTI', 'VNQ']
start_date = '2019-01-01'
end_date = '2024-01-01'

data = vt.get_data(stocks, start_date, end_date)
returns = data.pct_change().dropna()
alpha = 95

mcc_weights = vt.OptimizePortfolioWeights(returns, 0.0).opt_mcc(alpha)

cvar_contributions = vt.cvar_contributions(mcc_weights, returns, alpha)
cvar_contributions
```


## plot_weights
```python
stocks=['WMT','AAPL','GOOGL','PG','XOM','KO','CMG','F']
start_date='2020-01-01'
end_date='2024-11-24'

data = vt.get_data(stocks, start_date, end_date)
returns = data.pct_change().dropna()
rf = 0.04413

min_var = vt.OptimizePortfolioWeights(returns, rf).opt_min_var()

vt.plot_weights(stocks, min_var)
```


## call_delta and put_delta
```python
S_call = 20.3
K_call = 20.43
r_call = 0.0425
sigma_call = 0.102
T_call = 1/12

S_put = 20.3
K_put = 20.2
r_put = 0.0425
sigma_put = 0.156
T_put = 1/12

delta_call = vt.BlackScholes().call_delta(S_call, K_call, r_call, sigma_call, T_call)
delta_put = vt.BlackScholes().put_delta(S_put, K_put, r_put, sigma_put, T_put)

delta_call, delta_put
```

```python
# Write in order S, K, r, sigma, T

call = [20.3, 20.43, 0.0425, 0.102, 1/12]
put = [20.3, 20.2, 0.0425, 0.156, 1/12]

delta_call = vt.BlackScholes().call_delta(*call)
delta_put = vt.BlackScholes().put_delta(*put)

delta_call, delta_put
```


## delta_hedge
```python
# Write in order S, K, r, sigma, T, N (money invested in each option)

info_call = [[20.3, 20.43, 0.0425, 0.102, 1/12, 23],
            [20.3, 20.52, 0.0425, 0.111, 1/12, 25],
            [20.3, 20.43, 0.0421, 0.297, 6/12, 17],
            [20.3, 20.52, 0.0421, 0.289, 6/12, 32]]

info_put = [[20.3, 20.2, 0.0425, 0.156, 1/12, 12],
            [20.3, 20, 0.0425, 0.153, 1/12, 16],
            [20.3, 20.2, 0.0421, 0.348, 6/12, 11],
            [20.3, 20, 0.0421, 0.378, 6/12, 17]]

# If N is in millions of dollar, then
hedge = vt.BlackScholes().delta_hedge(info_call, info_put)
print(f'Buy {hedge} millions of dollars of the underlying asset')
```


## Bond
```python
# Create a 5-year bond with 6% annual coupon, priced at 8% yield
bond = vt.Bond(
    face_value=1000,
    coupon_rate=0.06,
    years_to_maturity=5,
    yield_to_maturity=0.08,
    payments_per_year=1
)

# Get bond price
price = bond.price()
print(f"Bond Price: ${price:.2f}")

# Get risk metrics
mac_dur = bond.macaulay_duration()
mod_dur = bond.modified_duration()
conv = bond.convexity()

print(f"Macaulay Duration: {mac_dur:.4f} years")
print(f"Modified Duration: {mod_dur:.4f}")
print(f"Convexity: {conv:.4f}")

# Estimate price change for +100bp yield increase
total_chg, dur_eff, conv_eff = bond.price_change_estimate(0.01)
print(f"Price change for +100bp: {total_chg*100:.2f}%")

# Print full summary
print(bond.summary())
```

```python
# Semi-annual coupon bond example
bond_semi = vt.Bond(
    face_value=1000,
    coupon_rate=0.05,
    years_to_maturity=10,
    yield_to_maturity=0.045,
    payments_per_year=2
)

print(f"Semi-annual bond price: ${bond_semi.price():.2f}")
print(f"Modified Duration: {bond_semi.modified_duration():.4f}")
```


## OptimizePortfolioWeights
```python
stocks=['WMT','AAPL','GOOGL','PG','XOM','KO','CMG','F']
start_date='2020-01-01'
end_date='2024-11-24'

data = vt.get_data(stocks, start_date, end_date)
returns = data.pct_change().dropna()
rf = 0.04413

opt_sharpe_weights = vt.OptimizePortfolioWeights(returns, rf).opt_max_sharpe()
opt_sharpe_weights
```


```python
tickers = ['NVDA','AMZN','AVGO','PG','V','RL','GLD']

benchmark = 'SPY'
start_date = '2025-01-01'
end_date = '2025-12-31'

price = vt.get_data(tickers, start_date, end_date)
benchmark_data = vt.get_data([benchmark], start_date, end_date)

rt_benchmark = benchmark_data.pct_change().dropna()
rt = price.pct_change().dropna()

min_semivar_weights = vt.OptimizePortfolioWeights(rt, 0.0).opt_min_semivar(rt_benchmark)
min_semivar_weights
```


## DynamicBacktesting
```python
stocks=['WMT','AAPL','GOOGL','PG','XOM','KO','CMG','F']
start_date='2020-01-01'
end_date='2024-11-24'

data = vt.get_data(stocks, start_date, end_date)
returns = data.pct_change().dropna()
rf = 0.0035
pv = 1_000_000.0
months = 2

history = vt.DynamicBacktesting(price, benchmark_data, capital=1_000_000, rf=rf, months=months).simulation()
history
```


## simulate_portfolio
```python
stocks = ["AAPL", "TSLA", "AMD", "LMT", "JPM"]
start_date = "2020-01-01"
end_date = "2023-01-01"

data = vt.get_data(stocks, start_date, end_date)
weights = [0.2, 0.2, 0.2, 0.2, 0.2]
days = 252
N = 10000

simulations = vt.simulate_portfolio(data, weights, days, N)

plt.figure(figsize=(10, 6))
plt.plot(simulations[:, :100], alpha=0.3)
plt.title("Simulated Portfolio Paths (Cholesky)")
plt.xlabel("Days")
plt.ylabel("Cumulative Value")
plt.show()
```


## License
This project is licensed under the GPL-3.0 license.

## Author
Luis Fernando Márquez Bañuelos
