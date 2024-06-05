import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime, timedelta

# get stock data
def get_stock_data(symbol, interval='1m', hours_back=24):
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=hours_back)
    return yf.download(symbol, interval=interval, start=start_date, end=end_date)

# Bollinger Bands strategy
def bollinger_bands_strategy(data, window=20, num_of_std=2):
    signals = pd.DataFrame(index=data.index)
    signals['price'] = data['Close']
    signals['middle_band'] = data['Close'].rolling(window=window).mean()
    signals['upper_band'] = signals['middle_band'] + (data['Close'].rolling(window=window).std() * num_of_std)
    signals['lower_band'] = signals['middle_band'] - (data['Close'].rolling(window=window).std() * num_of_std)
    signals['signal'] = 0.0
    signals['signal'][window:] = np.where(signals['price'][window:] > signals['upper_band'][window:], -1.0, np.where(signals['price'][window:] < signals['lower_band'][window:], 1.0, 0.0))
    signals['positions'] = signals['signal'].diff()
    return signals

def update(frame):
    new_data = get_stock_data(stock_symbol, interval='1m', hours_back=30)
    signals = bollinger_bands_strategy(new_data)

    plt.clf()

    plt.plot(new_data['Close'], label=f'{stock_symbol} Price')
    plt.plot(signals['middle_band'], label='Middle Band', linestyle='--')
    plt.plot(signals['upper_band'], label='Upper Band', linestyle='--')
    plt.plot(signals['lower_band'], label='Lower Band', linestyle='--')

    buy_indices = signals.loc[signals.positions == 1.0].index
    sell_indices = signals.loc[signals.positions == -1.0].index

    plt.scatter(buy_indices, new_data.loc[buy_indices]['Close'], marker='^', color='g', label='Buy', alpha=1, s=100)
    plt.scatter(sell_indices, new_data.loc[sell_indices]['Close'], marker='v', color='r', label='Sell', alpha=1, s=100)

    plt.title(f'{stock_symbol} - Real-Time Bollinger Bands Strategy')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()

stock_symbol = 'AAPL'

fig, ax = plt.subplots(figsize=(12, 8))
ani = FuncAnimation(fig, update, interval=120000) # adjustable (120sec)
plt.show()
