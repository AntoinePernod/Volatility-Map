import dash_table
import numpy as np
import pandas as pd
import datetime as dt
import yfinance as yf
import matplotlib.pyplot as plt
import dash
from dash import dcc,html,Input,Output, dash_table
import plotly.express as px

def options_data(ticker):
    asset = yf.Ticker(ticker)
    option_exp_dates = asset.options
    print(option_exp_dates)

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

        options_chain = pd.concat([options_chain, chain])

    return options_chain

app = dash.Dash(__name__)
app.title = 'Volatility Dashboard'

app.layout = [
    html.Div(children='Options Data',style={'textAlign':'center','fontsize':24}),
    dash_table.DataTable(data=options_data('SPY').to_dict('records'),
                         columns=[{'name': i, 'id': i} for i in options_data('SPY').columns]),
    dcc.Graph(figure=px.histogram(options_data('SPY'),x='Expiry', y='impliedVolatility',title='Expiry Distribution', histfunc='avg'))]



if __name__ == '__main__':
    app.run(debug=True)
