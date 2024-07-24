from flask import Flask, request, render_template
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64
import requests  # Import requests to make HTTP requests

app = Flask(__name__)

API_KEY = 'PZLREYE2QUALWZHR'  # Your Alpha Vantage API key

def fetch_earnings_dates(ticker):
    """Fetch earnings dates and EPS data for a given stock ticker using Alpha Vantage."""
    url = f'https://www.alphavantage.co/query?function=EARNINGS_CALENDAR&symbol={ticker}&apikey={API_KEY}&horizon=12m'
    response = requests.get(url)
    data = response.json()
    earnings = []
    if 'data' in data:
        for item in data['data']:
            if 'fiscalDateEnding' in item and 'reportedEPS' in item:
                earnings.append({
                    'Date': item['fiscalDateEnding'],
                    'Actual EPS': item['reportedEPS'],
                    'Expected EPS': item.get('estimatedEPS', 'N/A')  # 'N/A' if not available
                })
    return earnings

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

    for date, row in earnings_data.iterrows():
        ax.annotate(f'Actual EPS: {row["Actual EPS"]}\nExpected EPS: {row["Expected EPS"]}',
                    xy=(date, data.at[date, 'Close'] if date in data.index else data.iloc[-1]['Close']),
                    xytext=(0, 30), textcoords="offset points",
                    ha='center', va='bottom', color='green' if row["Actual EPS"] >= row["Expected EPS"] else 'red',
                    arrowprops=dict(arrowstyle='->', color='black'))

    ax.set_title(f'Stock Prices and Earnings Data for {ticker}')
    ax.set_xlabel('Date')
    ax.set_ylabel('Close Price')
    plt.legend()
    plt.grid(True)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')

    return render_template('plot.html', plot_url=plot_url)

if __name__ == '__main__':
    app.run(debug=True)