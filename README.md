# VaR Calculation Library

## Overview
This Python library provides functions to calculate the **Value at Risk (VaR)** and **Conditional Value at Risk (cVaR)** for financial portfolios, including stock and forex portfolios. These risk measures help in understanding potential losses under given confidence levels.

## Features
- Calculate **VaR** and **cVaR** for a **stock portfolio**.
- Calculate **VaR** and **cVaR** for a **forex portfolio**.
- Supports both **long** and **short** positions.
- Outputs results in both **percentage** and **cash value**.

## Installation
Ensure you have the required dependencies installed:

```bash
pip install numpy 
pip install pandas
```

## Functions

### `var_stocks(data, stocks, n_stocks, conf, long)`
Calculates the **VaR** and **cVaR** for a stock portfolio.

#### Parameters:
- `data` (*pd.DataFrame*): DataFrame containing stock prices.
- `stocks` (*list*): List of stock tickers.
- `n_stocks` (*list*): Number of stocks per ticker.
- `conf` (*float*): Confidence level (e.g., 95 for 95%).
- `long` (*bool*): `True` for long position, `False` for short position.

#### Returns:
A DataFrame with the following columns:
- **Métrica**: "VaR" and "cVaR".
- **Porcentaje**: The percentage value of risk.
- **Cash**: The risk in monetary terms.

### `var_forex(data, currencies, positions, conf, long)`
Calculates the **VaR** and **cVaR** for a forex portfolio.

#### Parameters:
- `data` (*pd.DataFrame*): DataFrame containing forex currency pair prices.
- `currencies` (*list*): List of currency pairs.
- `positions` (*list*): Number of units per currency pair.
- `conf` (*float*): Confidence level (e.g., 95 for 95%).
- `long` (*bool*): `True` for long position, `False` for short position.

#### Returns:
A DataFrame with the following columns:
- **Métrica**: "VaR" and "cVaR".
- **Porcentual**: The percentage value of risk.
- **Cash**: The risk in monetary terms.

## Usage Example
```python
import pandas as pd
import numpy as np
from vartools import var_stocks, var_forex  # Replace with actual import path

# Example data
stock_data = pd.DataFrame({...})  # Stock price data, you can use yfinance
tickers = ['AAPL', 'GOOGL', 'MSFT']
n_shares = [10, 5, 8]
confidence = 95
is_long = True

# Calculate stock portfolio VaR
stock_var = var_stocks(stock_data, tickers, n_shares, confidence, is_long)
print(stock_var)

# Example forex data
forex_data = pd.DataFrame({...})  # Forex currency pair data, you can use yfinance
currency_pairs = ['EUR/USD', 'GBP/USD']
positions = [10000, 5000]

# Calculate forex portfolio VaR
forex_var = var_forex(forex_data, currency_pairs, positions, confidence, is_long)
print(forex_var)
```

## License
This project is licensed under the GPL-3.0 license.

## Author
Luis Fernando Márquez Bañuelos
