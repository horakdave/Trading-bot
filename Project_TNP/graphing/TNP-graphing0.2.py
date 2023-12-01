import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from datetime import datetime, timedelta

def get_stock_data(symbol, interval='1m', hours_back=30):
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=hours_back)
    return yf.download(symbol, interval=interval, start=start_date, end=end_date)

def simple_moving_average_strategy(data, short_window=10, long_window=50):
    signals = pd.DataFrame(index=data.index)
    signals['price'] = data['Close']
    signals['short_mavg'] = data['Close'].rolling(window=short_window, min_periods=1, center=False).mean()
    signals['long_mavg'] = data['Close'].rolling(window=long_window, min_periods=1, center=False).mean()
    signals['signal'] = 0.0
    signals['signal'][short_window:] = np.where(signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1.0, 0.0)
    signals['positions'] = signals['signal'].diff()
    return signals

def update(frame):
    new_data = get_stock_data(stock_symbol, interval='1m', hours_back=30)
    signals = simple_moving_average_strategy(new_data)

    plt.clf()
    plt.plot(new_data['Close'], label=f'{stock_symbol} Price')
    plt.plot(signals['short_mavg'], label='Short MA')
    plt.plot(signals['long_mavg'], label='Long MA')
    plt.plot(signals.loc[signals.positions == 1.0].index, signals.short_mavg[signals.positions == 1.0], '^', markersize=10, color='g', label='Buy')
    plt.plot(signals.loc[signals.positions == -1.0].index, signals.short_mavg[signals.positions == -1.0], 'v', markersize=10, color='r', label='Sell')

    plt.title(f'{stock_symbol} - Real-Time Moving Average Strategy')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()

stock_symbol = 'TSLA'

fig, ax = plt.subplots(figsize=(12, 8))
ani = FuncAnimation(fig, update, interval=5000)  # update on 5 secs(adjustable)
plt.show()
