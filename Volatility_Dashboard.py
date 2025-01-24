import dash_table
import numpy as np
import pandas as pd
import datetime as dt
import yfinance as yf
import matplotlib.pyplot as plt
import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
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

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = 'Volatility Dashboard'

app.layout = html.Div([
    html.Div([
        html.H1(children='Options Data', style={'textAlign': 'center', 'fontsize': 24}),
        html.Div([
            html.Label('Ticker Symbol'),
            dcc.Input(id='ticker-input', type='text', value='SPY', placeholder='Enter Ticker Symbol', debounce=True),
            # html.Button('Submit',id='submit-val',n_clicks=0)
        ], style={"margin-bottom": "20px"}),

        html.Div([
            html.Label("Select Expiry Date"),
            dcc.Dropdown(id="expiry-dropdown", placeholder="Select Expiry Date")
        ], style={"margin-bottom": "40px"}),

        html.Div([
            html.Label("Volatility Skew"),
            dcc.Graph(id='volatility-skew'),
        ], style={"margin-bottom": "40px"}),

        html.Div([
            html.Label("Volatility Surface"),
            dcc.Graph(id='volatility-surface'),
        ], style={'textAlign': 'center'}),
    ], style={"width": "80%", "margin": "0 auto"}),
])

app.callback(
    Output('expiry-dropdown', 'options'),
    Output('expiry-dropdown', 'value'),
    Input('ticker-input', 'value')
)

def update_expriry_dates(ticker):
    options = options_data(ticker)
    expiry_dates = options['Expiry'].unique()
    return [{'label': date, 'value': date} for date in expiry_dates], expiry_dates[0] if len(expiry_dates) > 0 else None

app.callback(
    Output('volatility-skew', 'figure'),
    Output('volatility-surface', 'figure'),
    Input('ticker-input', 'value'),
    Input('expiry-dropdown', 'value')

)

# dash_table.DataTable(data=options_data('SPY').to_dict('records'),
#                      columns=[{'name': i, 'id': i} for i in options_data('SPY').columns]),
# dcc.Graph(figure=px.histogram(options_data('SPY'),x='Expiry', y='impliedVolatility',title='Expiry Distribution', histfunc='avg'))]



if __name__ == '__main__':
    app.run(debug=True)
