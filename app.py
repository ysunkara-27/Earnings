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
    data = stock.history(start='2020-01-01')
    data.index = data.index.tz_localize(None)

    # Define earnings dates, actual EPS, and expected EPS values
    earnings_info = {
        'Date': ['2023-02-02', '2023-05-01', '2023-07-25', '2023-10-26', '2024-02-01', '2024-05-01'],
        'Actual EPS': [10.58, 11.90, 12.34, 13.10, 14.25, 15.40],
        'Expected EPS': [10.50, 12.00, 12.30, 13.00, 14.20, 15.35]
    }
    earnings_data = pd.DataFrame(earnings_info)
    earnings_data['Date'] = pd.to_datetime(earnings_data['Date'])
    earnings_data.set_index('Date', inplace=True)

    # Prepare data for plotting
    segmented_data = pd.DataFrame()
    pre_window = 7  # days before the earnings to start the analysis
    post_window = 7  # days after the earnings to end the analysis

    for date in earnings_data.index:
        window_start = date - pd.Timedelta(days=pre_window)
        window_end = date + pd.Timedelta(days=post_window)
        segment = data.loc[window_start:window_end]
        segment['Segment'] = f'{date.strftime("%Y-%m-%d")}'
        segmented_data = pd.concat([segmented_data, segment])

    # Plotting
    fig, ax = plt.subplots(figsize=(20, 7))
    for key, grp in segmented_data.groupby('Segment'):
        ax.plot(grp.index, grp['Close'], marker='o', label=key)

    # Annotate with EPS and percentage changes
    for date, row in earnings_data.iterrows():
        close_start = segmented_data.loc[date - pd.Timedelta(days=pre_window), 'Close']
        close_end = segmented_data.loc[date + pd.Timedelta(days=post_window), 'Close']
        percent_change = ((close_end - close_start) / close_start) * 100
        ax.annotate(f'Actual EPS: {row["Actual EPS"]}\nExpected EPS: {row["Expected EPS"]}',
                    xy=(date, ax.get_ylim()[1]), xytext=(0, 30), textcoords="offset points",
                    ha='center', va='bottom', color='black', arrowprops=dict(arrowstyle='-[, widthB=2.5, lengthB=1.5', lw=1.5))
        ax.annotate(f'{percent_change:.2f}%', xy=(date, close_end),
                    xytext=(0, -20), textcoords="offset points", ha='center', color='blue')

    # Convert plot to PNG image to send to HTML
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')

    return render_template('plot.html', plot_url=plot_url)

if __name__ == '__main__':
    app.run(debug=True)