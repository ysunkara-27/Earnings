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
    data = yf.Ticker(ticker).history(start='2020-01-01')
    data.index = data.index.tz_localize(None)

    # Dummy earnings data, replace with real data fetching in production
    earnings_info = {
        'Date': ['2023-02-02', '2023-05-01'],
        'Actual EPS': [10.58, 11.90],
        'Expected EPS': [10.50, 12.00]
    }
    earnings_data = pd.DataFrame(earnings_info)
    earnings_data['Date'] = pd.to_datetime(earnings_data['Date'])
    earnings_data.set_index('Date', inplace=True)

    fig, ax = plt.subplots()
    ax.plot(data.index, data['Close'])
    ax.set_title(f'Stock Prices for {ticker}')
    ax.set_xlabel('Date')
    ax.set_ylabel('Close Price')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')

    return render_template('plot.html', plot_url=plot_url)

if __name__ == '__main__':
    app.run(debug=True)
