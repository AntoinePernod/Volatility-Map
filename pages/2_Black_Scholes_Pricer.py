import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Black-Scholes Calculator", layout="wide")
st.title("⚖️ Black-Scholes Option Pricing Calculator")

udl = st.text_input("Ticker", "SPY").upper()
asset = yf.Ticker(udl)
spot_price = asset.history(period='1d')['Close'].iloc[-1]
st.write(f"Current Spot Price: ${spot_price:.2f}")

strike_price = st.number_input("Strike Price", min_value=0.01, value=spot_price)
time_to_expiry = st.number_input("Time to Expiry (in years)", min_value=0.01, value=1)