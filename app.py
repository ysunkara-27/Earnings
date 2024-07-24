from flask import Flask, request, render_template
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot():
    ticker = request.form['ticker']
    stock = yf.Ticker(ticker)

    # Fetch stock history and earnings data
    data = stock.history(period="max")
    earnings = stock.earnings

    # If earnings data is available, use the last entry as an example
    if not earnings.empty:
        actual_eps = earnings.iloc[-1]['Earnings']
        expected_eps = "N/A"  # This should be fetched or calculated based on another reliable source if available
    else:
        actual_eps = "Data Unavailable"
        expected_eps = "Data Unavailable"

    # Generate the stock price chart
    fig, ax = plt.subplots(figsize=(10, 5))
    data['Close'].plot(ax=ax)
    ax.set_title(f'Stock Prices for {ticker}')
    ax.set_xlabel('Date')
    ax.set_ylabel('Close Price')
    plt.grid(True)

    # Convert plot to PNG image to send to HTML
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')

    # Send the data to the HTML template
    return render_template('plot.html', plot_url=plot_url, ticker=ticker, actual_eps=actual_eps, expected_eps=expected_eps)

if __name__ == '__main__':
    app.run(debug=True)