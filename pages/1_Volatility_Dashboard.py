import streamlit as st
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd

import utils.functions as funcs

st.set_page_config(page_title="📊 Volatility Dashboard", layout="wide")
st.title("📊 Volatility Dashboard")

col1, col2 = st.columns([1,2])

with col1:
    ticker = st.text_input("Enter Ticker: ", "SPY").upper()

    options, spot = funcs.options_data(ticker)
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


    merged_iv = funcs.merge_iv(filtered_calls_at_expiry, filtered_puts_at_expiry, spot).sort_values(by='strike', ascending=True)
    print(merged_iv.head())

    st.metric(label="Spot Price", value=f"${spot:,.2f}")
    # st.write(f"Selected Expiry Date: {expiry_selected}")
    st.dataframe(merged_iv)

    skew_figure = st.line_chart(merged_iv.set_index('percentStrike')['impliedVolatility'], x_label='Strike (%)', y_label='Implied Volatility')
    
    
    
with col2:

    fig = plt.figure(figsize=(10,4))
    plt.plot(filtered_calls_at_expiry['percentStrike'], filtered_calls_at_expiry['impliedVolatility'], label='Calls', color='blue')
    plt.plot(filtered_puts_at_expiry['percentStrike'], filtered_puts_at_expiry['impliedVolatility'], label='Puts', color='orange')
    plt.xlabel('Strike')
    plt.ylabel('Implied Volatility')
    plt.title(f'Implied Volatility Skew for {ticker} Options Expiring on {expiry_selected}')
    plt.legend()
    st.pyplot(fig)