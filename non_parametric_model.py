import yfinance as yf
import pandas as pd
import numpy as np

# Define your portfolio
portfolio = pd.DataFrame({
    'Company': ['Apple Inc.', 'Microsoft Corporation', 'Amazon.com Inc.', 'NVIDIA Corporation', 'Alphabet Inc. Class A'],
    'Symbol': ['AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOGL'],
    'Quantity': [10000, 15000, 8000, 5000, 9000]
})

# Set the risk parameters
risk_horizon = 1
confidence_level_var = 0.99
confidence_level_es = 0.975
num_observations = 500

# Set the as-of date
as_of_date = pd.to_datetime('2022-12-30')


# Function to calculate VaR and ES
def calculate_var_es(symbols, quantities, currency):
    #print("symbols:", list(symbols))
    try:
        months = int((num_observations - 1) / 30)
        start = as_of_date - pd.DateOffset(months=months)
        symbol_data = yf.download(list(symbols), start=start, end=as_of_date)
        prices = symbol_data['Adj Close']
        print(prices)

        # Retrieve EUR/USD forex prices
        forex_data = yf.download('EURUSD=X', start=start, end=as_of_date)
        forex_prices = forex_data['Adj Close']

        print(prices)
        print(forex_prices)
        print(type(forex_prices))

        # Convert prices to EUR if necessary
        if currency != 'EUR':
            prices = prices.multiply(forex_prices, axis=0)

        # Calculate daily returns
        returns = np.log(prices / prices.shift(1)).dropna()

        # Calculate portfolio returns
        portfolio_returns = returns.dot(quantities.values)

        # Order portfolio returns
        sorted_returns = np.sort(portfolio_returns)

        # Calculate VaR
        var_index = int(num_observations * (1 - confidence_level_var))
        var = -sorted_returns[var_index]

        # Calculate ES
        es_returns = sorted_returns[:var_index]
        es = -np.mean(es_returns)

        # Return VaR and ES
        return {'VaR': var, 'ES': es}
    except Exception as e:
        print("Error occurred while retrieving data for symbols:", symbols)
        print(e)
        return {'VaR': None, 'ES': None}


# Calculate VaR and ES for each risk type
risk_types = ['TOTAL', 'EQUITY', 'FOREX']
results = {}

for risk_type in risk_types:
    if risk_type == 'TOTAL':
        print("TOTAL:")
        # Calculate VaR and ES for the entire portfolio
        var_es = calculate_var_es(portfolio['Symbol'], portfolio['Quantity'], 'USD')
    elif risk_type == 'EQUITY':
        print("EQUITY:")
        # Calculate VaR and ES for equity only
        equity_symbols = portfolio.loc[~portfolio['Symbol'].str.startswith('GOOGL'), 'Symbol']
        equity_quantities = portfolio.loc[~portfolio['Symbol'].str.startswith('GOOGL'), 'Quantity']
        var_es = calculate_var_es(equity_symbols, equity_quantities, 'USD')
    elif risk_type == 'FOREX':
        # Calculate VaR and ES for forex exposure
        forex_symbol = 'EURUSD=X'
        print("FOREX:")
        forex_quantity = ['EURUSD=X'] * portfolio.loc[portfolio['Symbol'].str.startswith('GOOGL'), 'Quantity'].sum()
        #print(forex_quantity)
        var_es = calculate_var_es(forex_symbol, forex_quantity, 'EUR')

    # Store the results
    results[risk_type] = var_es

# Print the results
for risk_type, result in results.items():
    print('Risk Type:', risk_type)
    print('VaR (99%):', result['VaR'])
    print('ES (97.5%):', result['ES'])
    print()
