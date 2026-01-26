import yfinance as yf
import pandas as pd
import datetime as dt


def get_histo(ticker, period="1mo", interval="1d"):
    asset = yf.Ticker(ticker)
    histo = asset.history(period=period, interval=interval)
    return histo


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

        calls['Type'] = "Call"
        puts['Type'] = "Put"

        chain = pd.concat([calls, puts])
        chain['Expiry'] = expiry
        chain['DaysToExpiry'] = (pd.to_datetime(chain['Expiry']) - dt.datetime.now()).dt.days
        chain['percentStrike'] = chain['strike'] / spot * 100

        options_chain = pd.concat([options_chain, chain])

    return options_chain, spot



def merge_iv(calls, puts, spot):
    filtered_calls = calls[(calls['strike'] >= spot)][['strike', 'percentStrike', 'impliedVolatility', 'lastPrice', 'percentChange']]
    filtered_puts = puts[(puts['strike'] < spot)][['strike', 'percentStrike', 'impliedVolatility', 'lastPrice', 'percentChange']]

    combined = pd.concat([filtered_calls, filtered_puts], ignore_index=True)
    combined.dropna(subset=['impliedVolatility'], inplace=True)

    return combined



