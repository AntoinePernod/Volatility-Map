import numpy as np
import pandas as pd
import datetime as dt
import yfinance as yf
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go


# Récupérer les données d'options
def options_data(ticker):
    asset = yf.Ticker(ticker)
    option_exp_dates = asset.options

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


# Initialiser l'application
app = dash.Dash(__name__, external_stylesheets=["https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css"])
app.title = "Options Dashboard"

# Layout du dashboard
app.layout = html.Div([
    html.Div([
        html.H1("Options Dashboard", style={"text-align": "center"}),
        html.Div([
            html.Label("Enter Ticker:"),
            dcc.Input(id="ticker-input", type="text", value="SPY", placeholder="Enter a ticker", debounce=True),
        ], style={"margin-bottom": "20px"}),

        html.Div([
            html.Label("Select Expiry Date:"),
            dcc.Dropdown(id="expiry-dropdown", placeholder="Select expiry date"),
        ], style={"margin-bottom": "20px"}),

        html.Div([
            html.Label("Volatility Skew"),
            dcc.Graph(id="volatility-skew"),
        ], style={"margin-bottom": "40px"}),

        html.Div([
            html.Label("Calls Volatility Surface"),
            dcc.Graph(id="calls-volatility-surface"),
        ], style={"margin-bottom": "40px"}),

        html.Div([
            html.Label("Puts Volatility Surface"),
            dcc.Graph(id="puts-volatility-surface"),
        ]),
    ], style={"width": "80%", "margin": "0 auto"}),
])


@app.callback(
    Output("expiry-dropdown", "options"),
    Output("expiry-dropdown", "value"),
    Input("ticker-input", "value")
)


def update_expiry_dates(ticker):
    try:
        options = options_data(ticker)
        expiry_dates = options["Expiry"].unique()
        return [{"label": date, "value": date} for date in expiry_dates], expiry_dates[0] if len(expiry_dates) > 0 else None
    except Exception as e:
        return [], None


@app.callback(
    Output("volatility-skew", "figure"),
    Output("calls-volatility-surface", "figure"),
    Output("puts-volatility-surface", "figure"),
    Input("ticker-input", "value"),
    Input("expiry-dropdown", "value")
)


def update_graphs(ticker, expiry_date):
    if not expiry_date:
        return {}, {}, {}

    try:
        options = options_data(ticker)
        calls = options[options['Type'] == 'Call']
        puts = options[options['Type'] == 'Put']

        calls_at_expiry = calls[calls['Expiry'] == expiry_date]
        puts_at_expiry = puts[puts['Expiry'] == expiry_date]

        filtered_calls = calls_at_expiry[calls_at_expiry['impliedVolatility'] >= 0.001]
        filtered_puts = puts_at_expiry[puts_at_expiry['impliedVolatility'] >= 0.001]

        skew_fig = go.Figure()
        if not filtered_calls.empty:
            skew_fig.add_trace(go.Scatter(x=filtered_calls['strike'], y=filtered_calls['impliedVolatility'], mode='lines', name='Calls'))
        if not filtered_puts.empty:
            skew_fig.add_trace(go.Scatter(x=filtered_puts['strike'], y=filtered_puts['impliedVolatility'], mode='lines', name='Puts'))
        skew_fig.update_layout(title=f"Implied Volatility Skew - {expiry_date}", xaxis_title="Strike", yaxis_title="Implied Volatility")

        calls_surface = calls[['strike', 'DaysToExpiry', 'impliedVolatility']].pivot_table(
            values='impliedVolatility', index='strike', columns='DaysToExpiry').dropna()
        X_calls, Y_calls = np.meshgrid(calls_surface.index, calls_surface.columns)
        Z_calls = calls_surface.values

        calls_fig = go.Figure(data=[go.Surface(z=Z_calls, x=X_calls, y=Y_calls, colorscale='Viridis')])
        calls_fig.update_layout(title="Calls Implied Volatility Surface", scene=dict(
            xaxis_title="Strike", yaxis_title="Days to Expiry", zaxis_title="Implied Volatility"))

        puts_surface = puts[['strike', 'DaysToExpiry', 'impliedVolatility']].pivot_table(
            values='impliedVolatility', index='strike', columns='DaysToExpiry').dropna()
        X_puts, Y_puts = np.meshgrid(puts_surface.index, puts_surface.columns)
        Z_puts = puts_surface.values

        puts_fig = go.Figure(data=[go.Surface(z=Z_puts, x=X_puts, y=Y_puts, colorscale='Plasma')])
        puts_fig.update_layout(title="Puts Implied Volatility Surface", scene=dict(
            xaxis_title="Strike", yaxis_title="Days to Expiry", zaxis_title="Implied Volatility"))

        return skew_fig, calls_fig, puts_fig

    except Exception as e:
        return {}, {}, {}


if __name__ == "__main__":
    app.run_server(debug=True)
