import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def get_stock_data(symbol, interval='1m', period='1d'):
    return yf.download(symbol, interval=interval, period=period)

def simple_moving_average_strategy(data, short_window=10, long_window=50):
    signals = pd.DataFrame(index=data.index)
    signals['price'] = data['Close']
    signals['short_mavg'] = data['Close'].rolling(window=short_window, min_periods=1, center=False).mean()
    signals['long_mavg'] = data['Close'].rolling(window=long_window, min_periods=1, center=False).mean()
    signals['signal'] = 0.0
    signals['signal'][short_window:] = np.where(signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1.0, 0.0)
    signals['positions'] = signals['signal'].diff()
    return signals

stock_symbol = 'TSLA'   #chose your own stock
stock_data = get_stock_data(stock_symbol, interval='1m', period='1d')

signals = simple_moving_average_strategy(stock_data)

plt.figure(figsize=(12, 8))
plt.plot(stock_data['Close'], label=f'{stock_symbol} Price')
plt.plot(signals['short_mavg'], label='Short MA')
plt.plot(signals['long_mavg'], label='Long MA')
plt.plot(signals.loc[signals.positions == 1.0].index, signals.short_mavg[signals.positions == 1.0], '^', markersize=10, color='g', label='Buy')
plt.plot(signals.loc[signals.positions == -1.0].index, signals.short_mavg[signals.positions == -1.0], 'v', markersize=10, color='r', label='Sell')

plt.title(f'{stock_symbol} - Simple Moving Average Strategy')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()
