import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime, timedelta

def get_stock_data(symbol, interval='1d', hours_back=24):   # adjust later
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=hours_back)
    return yf.download(symbol, interval=interval, start=start_date, end=end_date)

def simple_moving_average_strategy(data, short_window=10, long_window=50):
    signals = pd.DataFrame(index=data.index)
    signals['price'] = data['Close']
    signals['short_mavg'] = data['Close'].rolling(window=short_window, min_periods=1, center=False).mean()
    signals['long_mavg'] = data['Close'].rolling(window=long_window, min_periods=1, center=False).mean()
    signals['signal'] = (signals['short_mavg'] > signals['long_mavg']).astype(float)
    signals['positions'] = signals['signal'].diff()
    return signals

def update(frame):
    global new_data, signals

    new_data = get_stock_data(stock_symbol, interval='1d', hours_back=30)
    signals = simple_moving_average_strategy(new_data)

    plt.clf()

    plt.plot(new_data['Close'], label=f'{stock_symbol} Price')

    if not signals.empty:
        plt.plot(signals['short_mavg'], label='Short MA', linestyle='-')
        plt.plot(signals['long_mavg'], label='Long MA', linestyle='-')

        buy_indices = signals.loc[signals.positions == 1.0].index
        buy_values = signals.short_mavg[signals.positions == 1.0]
        plt.scatter(buy_indices, buy_values, marker='^', color='g', label='Buy', alpha=1, s=100)

        sell_indices = signals.loc[signals.positions == -1.0].index
        sell_values = signals.short_mavg[signals.positions == -1.0]
        plt.scatter(sell_indices, sell_values, marker='v', color='r', label='Sell', alpha=1, s=100)

    # profit/loss
    for index, row in signals.iterrows():
        if row['positions'] == 1.0:
            profit_loss = new_data.loc[index:, 'Close'].pct_change().sum()
            plt.text(index, new_data.loc[index, 'Close'], f'{profit_loss * 100:.2f}%', color='g', fontsize=10, ha='right')
        elif row['positions'] == -1.0:
            profit_loss = new_data.loc[index:, 'Close'].pct_change().sum()
            plt.text(index, new_data.loc[index, 'Close'], f'{profit_loss * 100:.2f}%', color='r', fontsize=10, ha='left')

    plt.title(f'{stock_symbol} - Real-Time Moving Average Strategy')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()

stock_symbol = 'TSLA' # chose your own stock
initial_data = get_stock_data(stock_symbol, interval='1d', hours_back=24) # adjust later
signals = simple_moving_average_strategy(initial_data)

fig, ax = plt.subplots(figsize=(12, 8))
ani = FuncAnimation(fig, update, interval=120000, blit=False, cache_frame_data=False)
plt.show(block=True)