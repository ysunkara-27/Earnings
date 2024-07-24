from flask import Flask, request, render_template
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64
import requests  # Import requests to make HTTP requests

app = Flask(__name__)

API_KEY = 'PZLREYE2QUALWZHR'  # Alpha Vantage API key

def fetch_earnings_dates(ticker):
    """Fetch earnings dates and EPS data for a given stock ticker using yfinance."""
    stock = yf.Ticker(ticker)
    earnings = stock.earnings
    eps_data = []

    # Get actual EPS from Yahoo Finance
    if not earnings.empty:
        for date, row in earnings.iterrows():
            eps_data.append({
                'Date': str(date.date()),
                'Actual EPS': row.get('Earnings', 'N/A')
            })

    # Attempt to fetch expected EPS from Alpha Vantage (additional logic might be needed)
    # This part can be omitted if not necessary, or you can integrate another service for forward EPS.
    return eps_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot():
    ticker = request.form['ticker']
    stock = yf.Ticker(ticker)
    data = stock.history(start='2020-01-01')
    data.index = data.index.tz_localize(None)

    earnings_info = fetch_earnings_dates(ticker)
    if not earnings_info:
        return "Earnings data not found for the specified ticker.", 404

    earnings_data = pd.DataFrame(earnings_info)
    earnings_data['Date'] = pd.to_datetime(earnings_data['Date'])
    earnings_data.set_index('Date', inplace=True)

    fig, ax = plt.subplots(figsize=(20, 7))
    ax.plot(data.index, data['Close'], marker='o', label='Close Price')

    # Annotate with EPS
    for date, row in earnings_data.iterrows():
        close_price = data.at[date, 'Close'] if date in data.index else data.iloc[-1]['Close']
        ax.annotate(f'Actual EPS: {row["Actual EPS"]}',
                    xy=(date, close_price), xytext=(0, 30), textcoords="offset points",
                    ha='center', va='bottom', color='green',
                    arrowprops=dict(arrowstyle='->', color='black'))

    ax.set_title(f'Stock Prices and Earnings Data for {ticker}')
    ax.set_xlabel('Date')
    ax.set_ylabel('Close Price')
    plt.legend()
    plt.grid(True)

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')

    return render_template('plot.html', plot_url=plot_url)

if __name__ == '__main__':
    app.run(debug=True)
