import pandas as pd
import datetime as dt
import yfinance as yf
import streamlit as st
from mpl_toolkits.mplot3d import Axes3D



@st.cache_data

# Récupérer les données d'options
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

############## DASHBOARD SETUP ##############

st.set_page_config(page_title="📊 Volatility Dashboard", layout="wide")
st.title("📊 Volatility Dashboard")

ticker = st.text_input("Enter Ticker: ", "SPY").upper()

options, spot = options_data(ticker)
# print(options.columns)
calls = options[options['Type'] == 'Call']
puts = options[options['Type'] == 'Put']


expiries = options['Expiry'].unique()
# print(expiries)
expiry_selected = st.selectbox("Select Expiry Date: ", expiries)


calls_at_expiry = calls[calls['Expiry'] == expiry_selected]
filtered_calls_at_expiry = calls_at_expiry.loc[(calls_at_expiry['impliedVolatility'] >= 0.001) & (calls_at_expiry['strike'] >= spot)]
puts_at_expiry = puts[puts['Expiry'] == expiry_selected]
filtered_puts_at_expiry = puts_at_expiry.loc[(puts_at_expiry['impliedVolatility'] >= 0.001) & (puts_at_expiry['strike'] < spot)]


merged_iv = merge_iv(filtered_calls_at_expiry, filtered_puts_at_expiry, spot).sort_values(by='strike', ascending=True)
print(merged_iv.head())

st.write(f"Spot Price: ${spot:.2f}")
# st.write(f"Selected Expiry Date: {expiry_selected}")
st.dataframe(merged_iv)

skew_figure = st.line_chart(merged_iv.set_index('percentStrike')['impliedVolatility'], x_label='Strike (%)', y_label='Implied Volatility')


