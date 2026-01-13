import streamlit as st
import datetime as dt

def global_sidebar():
    st.sidebar.title("⚙️ Global Settings")
    ticker = st.sidebar.text_input("Enter Ticker: ", "SPY").upper()
    return ticker