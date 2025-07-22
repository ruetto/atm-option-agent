import os
import smtplib
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from utils import get_ticker_list, get_atm_data

SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")
FROM_NAME = os.getenv("FROM_NAME", "Option Agent")

def send_email(html):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Top 30 ATM Option Price Gaps"
    msg['From'] = FROM_NAME
    msg['To'] = EMAIL_TO
    part = MIMEText(html, 'html')
    msg.attach(part)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, EMAIL_TO, msg.as_string())

def run_agent():
    tickers = get_ticker_list()
    all_results = []
    for ticker in tickers:
        try:
            atm_rows = get_atm_data(ticker)
            all_results.extend(atm_rows)
        except Exception as e:
            print(f"Failed {ticker}: {e}")
    df = pd.DataFrame(all_results)
    df = df.sort_values(by='pct_gap', ascending=False).head(30)
    html = df.to_html(index=False, float_format="%.2f")
    send_email(html)

if __name__ == "__main__":
    run_agent()