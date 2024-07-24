from flask import Flask, request, render_template
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64
import requests  # Import requests to make HTTP requests

app = Flask(__name__)

# Replace 'YOUR_ALPHA_VANTAGE_API_KEY' with your actual Alpha Vantage API key.
API_KEY = 'PZLREYE2QUALWZHR'

def fetch_earnings_dates(ticker):
    url = f'https://www.alphavantage.co/query?function=EARNINGS_CALENDAR&symbol={ticker}&apikey={API_KEY}&horizon=12m'
    response = requests.get(url)
    data = response.json()
    print("API Response:", data)  # Ensure this prints detailed info for diagnosis

    earnings = []
    if 'data' in data:
        for item in data['data']:
            earnings.append({
                'Date': item.get('fiscalDateEnding', 'No Date'),
                'Actual EPS': item.get('reportedEPS', 'No Data'),
                'Expected EPS': item.get('estimatedEPS', 'No Data')
            })
    else:
        print("Error: Failed to fetch or parse earnings data.")
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

    # Annotate with EPS and percentage changes
    for date, row in earnings_data.iterrows():
        if date in data.index:
            close_price = data.at[date, 'Close']
        else:
            close_price = data.iloc[-1]['Close']  # Fallback to the last available close price if the date is out of range
        percent_change = ((close_price - data.iloc[0]['Close']) / data.iloc[0]['Close']) * 100  # Calculate percent change from the start
        ax.annotate(f'Actual EPS: {row["Actual EPS"]}\nExpected EPS: {row["Expected EPS"]}',
                    xy=(date, close_price), xytext=(0, 30), textcoords="offset points",
                    ha='center', va='bottom', color='green' if row["Actual EPS"] >= row.get("Expected EPS", row["Actual EPS"]) else 'red',
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
