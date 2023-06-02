import yfinance as yf
import pandas as pd
import numpy as np

# Define your portfolio
portfolio = pd.DataFrame({
    'Company': ['Apple Inc.', 'Microsoft Corporation', 'Amazon.com Inc.', 'NVIDIA Corporation', 'Alphabet Inc. Class A'],
    'Symbol': ['AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOGL'],
    'Quantity': [10000, 15000, 8000, 5000, 9000]
})

# portfolio = {
#    'AAPL': 10000,
#    'MSFT': 15000,
#    'AMZN': 8000,
#    'NVDA': 5000,
#    'GOOGL': 9000
#}

# Set the risk parameters
risk_horizon = 1
confidence_level_var = 0.99
confidence_level_es = 0.975
num_observations = 500

data = yf.download("msft aapl amzn nvda googl")

forex_data = yf.download('EURUSD=X')

# Add the column forex adj close and assign each row of the stock price data the correct forex rate
data['Forex Adj Close'] = None
for index, row in data.iterrows():
    try:
        data.at[index, 'Forex Adj Close'] = forex_data['Adj Close'][forex_data.index.get_loc(index)]
    except KeyError:
        continue

# Select 500 stock prices prior to 2022-12-30, including 2022-12-30
as_of_date_index = data.index.get_loc('2022-12-30')
start_date_index = as_of_date_index - 500
final_data = data[start_date_index:as_of_date_index + 1].copy()

# Set the stock prices and forex rates
stock_prices = final_data['Adj Close']
forex_rates = final_data['Forex Adj Close']

# Calculate the daily returns for stocks and forex
stock_returns = stock_prices.pct_change().dropna()
forex_returns = forex_rates.pct_change().dropna()

# Define the quantities of shares
quantities = [10000, 15000, 8000, 5000, 9000]

# Calculate the daily portfolio returns
portfolio_returns = (stock_returns * quantities).sum(axis=1)

# Calculate the VaR and ES for the total risk
var_total = -np.percentile(portfolio_returns, (1 - confidence_level_var) * 100)
es_total = -portfolio_returns[portfolio_returns <= -var_total].mean()

# Calculate the VaR and ES for the equity risk
var_equity = -np.percentile(portfolio_returns, (1 - confidence_level_var) * 100)
es_equity = -portfolio_returns[portfolio_returns <= -var_equity].mean()

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