import yfinance as yf
import requests
import pandas as pd
from datetime import datetime

def get_ticker_list():
    sp500_url = "https://datahub.io/core/s-and-p-500-companies/r/constituents.csv"
    nasdaq100_url = "https://en.wikipedia.org/wiki/NASDAQ-100"
    etf_url = "https://etfdb.com/compare/market-cap/"

    sp500 = pd.read_csv(sp500_url)["Symbol"].tolist()
    nasdaq = pd.read_html(nasdaq100_url)[4]["Ticker"].tolist()
    etfs = pd.read_html(etf_url)[0]["Symbol"].head(200).tolist()
    return sorted(set(sp500 + nasdaq + etfs))

def get_atm_data(ticker):
    stock = yf.Ticker(ticker)
    price = stock.history(period="1d")["Close"].iloc[-1]
    results = []
    for expiry in stock.options[:10]:
        chain = stock.option_chain(expiry)
        calls = chain.calls
        puts = chain.puts
        atm_strike = min(calls['strike'], key=lambda x: abs(x - price))
        call = calls[calls['strike'] == atm_strike]['lastPrice'].values[0]
        put = puts[puts['strike'] == atm_strike]['lastPrice'].values[0]
        pct_gap = abs(call - put) / price * 100
        results.append({
            "symbol": ticker,
            "expiration": expiry,
            "call_price": call,
            "put_price": put,
            "pct_gap": pct_gap
        })
    return results