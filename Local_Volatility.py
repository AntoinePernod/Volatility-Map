import pandas as pd
import datetime as dt
from datetime import datetime, timezone
import yfinance as yf


# Get options data from Yahoo Finance
def options_data(ticker):
    asset = yf.Ticker(ticker)
    option_exp_dates = asset.options
    print(option_exp_dates)

    options_chain = pd.DataFrame()

    for expiry in option_exp_dates:
        try:
            data = asset.option_chain(expiry)
            calls = data.calls
            puts = data.puts

            print(expiry)
            print(calls.head())
            print(puts.head())

            calls['Type'] = "Call"
            puts['Type'] = "Put"

            chain = pd.concat([calls, puts])
            chain['Expiry'] = expiry

            now = datetime.now(timezone.utc).replace(tzinfo=None)
            chain['DaysToExpiry'] = (pd.to_datetime(chain['Expiry']) - now).dt.days

            options_chain = pd.concat([options_chain, chain])
        except Exception as e:
            print(f"Erreur lors de la récupération de {expiry} : {e}")

    # Supprimer les timezones pour Excel
    for col in options_chain.select_dtypes(include=['datetimetz']).columns:
        options_chain[col] = options_chain[col].dt.tz_localize(None)

    options_chain.to_excel(f"{ticker}_options_data.xlsx", index=False)
    return options_chain


options = options_data('SPY')
