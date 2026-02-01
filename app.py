import streamlit as st
import yfinance as yf
import pandas as pd
import datetime as dt

import utils.sidebar
import utils.functions as funcs

import matplotlib.pyplot as plt
import plotly.graph_objects as go
import feedparser


### RSS Feed Parser

feeds = {
    'Reuters': 'https://www.reuters.com/markets/rss',
    'Bloomberg': 'https://www.bloomberg.com/markets/rss',
    'CNBC': 'https://www.cnbc.com/world-markets/rss/',
    'LeMonde': 'https://www.lemonde.fr/international/rss_full.xml'
}

st.set_page_config(page_title="📈 Market Overview", layout="wide")
st.title("📈 Market Overview Dashboard")
st.write("Work in progress...")
st.divider()



########################
st.subheader("🌍 Global Equity Indices")

indices = {
    "CAC 40": "^FCHI",
    "FTSE 100": "^FTSE",
    "DAX": "^GDAXI",
    "S&P 500": "^GSPC",
    "Dow Jones": "^DJI",
    "Nasdaq": "^IXIC",
    "Hang Seng": "^HSI",
    "Nikkei 225": "^N225"}

clos = st.columns(len(indices))

for i, (name, ticker) in enumerate(indices.items()):
    data = funcs.get_histo(ticker, period="5d", interval="1d")
    latest_close = data["Close"].iloc[-1]
    prev_close = data["Close"].iloc[-2]
    perf = (latest_close/ prev_close -1) *100

    with clos[i]:
        st.metric(label=name, value=f"{latest_close:,.2f}", delta=f"{perf:.2f}%")

st.divider()

########################
col_vol, news_col = st.columns([2,2])

with col_vol:
    st.subheader("📈 VIX Index")

    vix_col1, vix_col2 = st.columns(2)
    with vix_col1:
        period = st.selectbox("Period: ", ["1wk", "1mo", "1y", "5y", "10y"], index=2)

    with vix_col2:
        interval = st.selectbox("Interval: ", ["1d", "1wk", "1mo"], index=0)


    vix_data = funcs.get_histo("^VIX", period=period, interval=interval)
    rolling_window = vix_data["Close"].count()
    print(rolling_window)
    print(vix_data['Close'].describe(), '\n')
    vix_mean = vix_data["Close"].rolling(window=rolling_window).mean().iloc[-1]
    last_vix = vix_data["Close"].iloc[-1]

    st.write(f"***Last VIX Value: {last_vix:.2f}***")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(vix_data.index, vix_data['Close'], label='VIX')
    ax.axhline(y=vix_mean, color='r', linestyle='--', label=f'Mean ({vix_mean:.2f})')
    ax.axhline(y=vix_data['Close'].quantile(0.25), color='g', linestyle=':', label='25th Percentile')
    ax.axhline(y=vix_data['Close'].quantile(0.75), color='b', linestyle=':', label='75th Percentile')
    # ax.axhline(y=vix_data['Close'].iloc[-1], color='orange', linestyle='-.', label='Last VIX Value')
    ax.set_title('VIX Index')
    ax.set_xlabel('Date')
    ax.set_ylabel('VIX Value')
    ax.tick_params(axis='x', rotation=45)
    ax.grid()
    ax.legend()
    st.pyplot(fig)

    # version avec plotly
    fig1 = go.Figure()
    fig1.update_layout(title='VIX Index')
    fig1.add_trace(go.Scatter(x=vix_data.index, y=vix_data['Close']))
    fig1.add_hline(y=vix_mean, line_dash="dash", line_color="red", annotation_text=f"Mean ({vix_mean:.2f})")
    fig1.add_hline(y=vix_data['Close'].quantile(0.25), line_dash='dot', line_color='green', annotation_text='25th Percentile')
    fig1.add_hline(y=vix_data['Close'].quantile(0.75), line_dash='dot', line_color='blue', annotation_text='75th Percentile')
    # fig1.add_hline(y=vix_data['Close'].iloc[-1], line_dash='dot', line_color='orange', annotation_text='Last VIX Value')
    fig1.update_xaxes(title_text='Date')
    fig1.update_yaxes(title_text='VIX Value')
    
    
    st.plotly_chart(fig1, use_container_width=True)


with news_col:
    st.subheader("🗞️ Market News")

    feed = feedparser.parse(feeds['LeMonde'])
    for entry in feed.entries[:5]:
        st.subheader(entry.title)
        st.write(f'**Date:** *{entry.published}*')
        st.write(entry.summary)
        st.write(f'[Read more]({entry.link})')
        st.divider()

st.divider()

st.subheader('💡 Economic Indicators')

econ_col1, econ_col2 = st.columns(2)

with econ_col1:
    st.write("**US Unemployment Rate**")
    unemployment_data = pd.read_csv('https://fred.stlouisfed.org/graph/fredgraph.csv?id=UNRATE', parse_dates=['observation_date'])
    unemployment_data.set_index('observation_date', inplace=True)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=unemployment_data.index, y=unemployment_data['UNRATE'], mode='lines', name='Unemployment Rate'))
    fig2.update_layout(title='US Unemployment Rate Over Time', xaxis_title='Date', yaxis_title='Unemployment Rate (%)')
    st.plotly_chart(fig2, use_container_width=True)

with econ_col2:
    st.write("**US GDP Growth Rate**")
    gdp_data = pd.read_csv('https://fred.stlouisfed.org/graph/fredgraph.csv?id=GDP', parse_dates=['observation_date'])
    gdp_data.set_index('observation_date', inplace=True)

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=gdp_data.index, y=gdp_data['GDP'], mode='lines', name='GDP Growth Rate'))
    fig3.update_layout(title='US GDP Growth Rate Over Time', xaxis_title='Date', yaxis_title='GDP Growth Rate (%)')
    st.plotly_chart(fig3, use_container_width=True)
    
st.divider()

