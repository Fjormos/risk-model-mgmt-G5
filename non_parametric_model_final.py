import yfinance as yf
import numpy as np
import pandas as pd
# Set the parameters
risk_horizon = 1  # day
risk_currency = 'EUR'
as_of_date = pd.to_datetime('2022-12-30')
num_observations = 500
# Set the confidence levels
confidence_level_var = 0.99
confidence_level_es = 0.975

# Define the symbols of the companies and the forex rate
symbols = ['AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOGL', 'EURUSD=X']


months = int((num_observations - 1) / 30)
start = as_of_date - pd.DateOffset(months=months)
# Set the as-of date
as_of_date = pd.to_datetime('2022-12-30')
# Retrieve historical data from Yahoo Finance
data = yf.download(symbols, start=start, end=as_of_date)

# Select the adjusted closing price for each symbol
prices = data['Adj Close']

# Separate the stock prices and forex rates
stock_prices = prices.iloc[:, :-1]
forex_rates = prices.iloc[:, -1]

# Calculate the daily returns for stocks and forex
stock_returns = stock_prices.pct_change().dropna()
forex_returns = forex_rates.pct_change().dropna()

# Define the quantities of shares
quantities = [10000, 15000, 8000, 5000, 9000]

# Calculate the daily portfolio returns
portfolio_returns = (stock_returns * quantities).sum(axis=1)

# Find the closest available date prior to the specified date
as_of_date = stock_returns.index[stock_returns.index <= as_of_date][-1]

# Calculate the number of observations to consider
start_index = stock_returns.index.get_loc(as_of_date) - num_observations + 1
end_index = stock_returns.index.get_loc(as_of_date)


# Select the historical returns for calibration
calibration_returns = portfolio_returns.iloc[start_index:end_index+1]



# Calculate the VaR and ES for the total risk
var_total = -np.percentile(calibration_returns, (1 - confidence_level_var) * 100)
es_total = -calibration_returns[calibration_returns <= -var_total].mean()

# Calculate the VaR and ES for the equity risk
var_equity = -np.percentile(calibration_returns, (1 - confidence_level_var) * 100)
es_equity = -calibration_returns[calibration_returns <= -var_equity].mean()

# Calculate the VaR and ES for the forex risk
var_forex = -np.percentile(forex_returns, (1 - confidence_level_var) * 100)
es_forex = -forex_returns[forex_returns <= -var_forex].mean()

print('Total Risk:')
print('VaR (99%):', var_total)
print('ES (97.5%):', es_total)

print('\nEquity Risk:')
print('VaR (99%):', var_equity)
print('ES (97.5%):', es_equity)

print('\nForex Risk:')
print('VaR (99%):', var_forex)
print('ES (97.5%):', es_forex)
