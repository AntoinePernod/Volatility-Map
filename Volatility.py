# import matplotlib
import numpy as np
import pandas as pd
import datetime as dt
import yfinance as yf
import matplotlib.pyplot as plt

# matplotlib.use('TkAgg')


# Get options data from Yahoo Finance
def options_data(ticker):
    asset = yf.Ticker(ticker)
    option_exp_dates = asset.options
    print(option_exp_dates)

    spot = asset.history(period='1d')['Close'].iloc[-1]
    options_chain = pd.DataFrame()

    for expiry in option_exp_dates:
        data = asset.option_chain(expiry)
        calls = data.calls
        puts = data.puts
        # print(expiry)
        # print(calls.head())
        # print(puts.head())

        calls['Type'] = "Call"
        puts['Type'] = "Put"

        chain = pd.concat([calls, puts])
        chain['Expiry'] = expiry
        chain['DaysToExpiry'] = (pd.to_datetime(chain['Expiry']) - dt.datetime.now()).dt.days

        options_chain = pd.concat([options_chain, chain])

    return options_chain, spot


options, spot = options_data('SPY')
print(f"Spot: , {spot:.2f}")

calls = options[options['Type'] == 'Call']
puts = options[options['Type'] == 'Put']

# Plotting Volatility Skew
expiry_date = '2026-01-16'
calls_at_expiry = calls[calls['Expiry'] == expiry_date]
filtered_calls_at_expiry = calls_at_expiry.loc[(calls_at_expiry['impliedVolatility'] >= 0.001) & (calls_at_expiry['strike'] >= spot)]
puts_at_expiry = puts[puts['Expiry'] == expiry_date]
filtered_puts_at_expiry = puts_at_expiry.loc[(puts_at_expiry['impliedVolatility'] >= 0.001) & (puts_at_expiry['strike'] < spot)]

print('Filtered Calls:', filtered_calls_at_expiry[['strike', 'impliedVolatility']])


if calls_at_expiry.empty:
    print('No data available for the selected expiry date')
else:
    filtered_calls_at_expiry.set_index('strike', inplace=True)
    filtered_calls_at_expiry['impliedVolatility'].plot(title=f'Implied Volatility Skew - {expiry_date}')
    filtered_puts_at_expiry.set_index('strike', inplace=True)
    filtered_puts_at_expiry['impliedVolatility'].plot()
    plt.xlabel('Strike')
    plt.ylabel('Implied Volatility')
    plt.legend(['Calls', 'Puts'])
    plt.show()


# Plotting Volatility Surfaces
calls_surface = calls[['strike', 'DaysToExpiry', 'impliedVolatility']].pivot_table(values='impliedVolatility', index='strike', columns='DaysToExpiry').dropna()
puts_surface = puts[['strike', 'DaysToExpiry', 'impliedVolatility']].pivot_table(values='impliedVolatility', index='strike', columns='DaysToExpiry').dropna()

# Calls Volatility Surface
fig_calls = plt.figure(figsize=(10, 8))
ax_calls = fig_calls.add_subplot(111, projection='3d')
X_calls, Y_calls = np.meshgrid(calls_surface.columns, calls_surface.index)
Z_calls = calls_surface.values

ax_calls.set_title('Calls Implied Volatility Surface')
ax_calls.set_xlabel('Days to Expiry')
ax_calls.set_ylabel('Strike')
ax_calls.set_zlabel('Implied Volatility')
ax_calls.plot_surface(X_calls, Y_calls, Z_calls, cmap='viridis')
plt.show()

# Puts Volatility Surface
fig_puts = plt.figure(figsize=(10, 8))
ax_puts = fig_puts.add_subplot(111, projection='3d')
X_puts, Y_puts = np.meshgrid(puts_surface.columns, puts_surface.index)
Z_puts = puts_surface.values

ax_puts.set_title('Puts Implied Volatility Surface')
ax_puts.set_xlabel('Days to Expiry')
ax_puts.set_ylabel('Strike')
ax_puts.set_zlabel('Implied Volatility')
ax_puts.plot_surface(X_puts, Y_puts, Z_puts, cmap='plasma')
plt.show()

