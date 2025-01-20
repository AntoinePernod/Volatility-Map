import numpy as np
import pandas as pd
import datetime as dt
import yfinance as yf
from scipy.stats import norm
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d


def options_data(ticker):
    asset = yf.Ticker(ticker)
    option_exp_dates = asset.options
    print(option_exp_dates)

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

    return options_chain


options = options_data('SPY')


calls = options[options['Type'] == 'Call']
puts = options[options['Type'] == 'Put']

expiry_date = '2025-01-21'
calls_at_expiry = calls[calls['Expiry'] == expiry_date]
print(calls_at_expiry.columns)

if calls_at_expiry.empty:
    print('No data available for the selected expiry date')
else:
    calls_at_expiry.set_index('strike', inplace=True)
    # calls_at_expiry['IV'] = calls_at_expiry['Implied Volatility'].str.rstrip('%').astype('float') / 100
    calls_at_expiry['impliedVolatility'].plot(title=f'IV Skew for Call expiring on {expiry_date}')
    plt.xlabel('Strike')
    plt.ylabel('Implied Volatility')
    plt.show()













############################################################################################################
# # Grid settings
# S_max = 200  # stock max
# S_min = 1e-4  # stock min, can't be 0 of pb w/ log()
# N = 100  # number of time steps
# M = 100  # nuber of stock steps
#
# # Time and Stock price
# T = 1
# dt = T / N
# dS = (S_max - S_min) / M
# t_grid = np.linspace(0, T, N + 1)
# S_grid = np.linspace(S_min, S_max, M + 1)
#
#
# # BS for european options
# def black_scholes(S,K, r, t, sigma, option_type):
#     d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * (T - t)) / (sigma * np.sqrt(T - t))
#     d2 = d1 - sigma * np.sqrt(T - t)
#     if option_type == 'call':
#         return S * norm.cdf(d1) - K * norm.cdf(d2) * np.exp(r * (T - t))
#     elif option_type == 'put':
#         return K * np.exp(r * (T - t)) * norm.cdf(-d2) - S * norm.cdf(-d1)
#     else:
#         print("Error !")
#         return 0
#
# """
# # Generate surface
# C = np.zeros((M + 1, N + 1))
# for i in range(M + 1):
#     for j in range(N + 1):
#         C[i, j] = black_scholes(S_grid[i], S_grid[j], 'call')
#
# D = np.zeros((M+1,N+1))
# for i in range(M+1):
#     for j in range(N+1):
#         C[i,j] = black_scholes(S_grid[i],S_grid[j],'put')
# """
# # Generate the surface
# C = np.zeros((M + 1, N + 1))
# for i in range(M + 1):
#     for j in range(N + 1):
#         C[i, j] = black_scholes(S_grid[i], t_grid[j],'call')
#
# D = np.zeros((M + 1, N + 1))
# for i in range(M + 1):
#     for j in range(N + 1):
#         C[i, j] = black_scholes(S_grid[i], t_grid[j],'put')
#
# print('Call Option Price:', "{:.2f}".format(black_scholes(110, 0, 'call')) + "€")
# print('Put Option Price:', "{:.2f}".format(black_scholes(110, 0, 'put')) + "€")
#
# # Plotting
# fig = plt.figure(figsize=(12, 8))
# ax = fig.add_subplot(111, projection='3d')
# S, T = np.meshgrid(S_grid, t_grid)
# ax.plot_surface(S, T, C.T, cmap='viridis')
# ax.set_xlabel('Stock Price')
# ax.set_ylabel('Time to Maturity')
# ax.set_zlabel('Option Price')
# ax.set_title('Black-Scholes Option Pricing Surface')
#
# # Rotate and adjust aspect ratio
# ax.view_init(elev=20, azim=210) # Adjust elevation and azimuthal angles
# ax.set_box_aspect([2, 1, 1]) # Adjust aspect ratio
#
# plt.show()
