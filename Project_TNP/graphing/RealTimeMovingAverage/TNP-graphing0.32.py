import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime, timedelta
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mpdates

def get_stock_data(symbol, interval='1m', hours_back=24):   # adjustable
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=hours_back) - timedelta(hours=0) # adjustable
    return yf.download(symbol, interval=interval, start=start_date, end=end_date)


def simple_moving_average_strategy(data, short_window=5, long_window=50):   #adjustable
    signals = pd.DataFrame(index=data.index)
    signals['price'] = data['Close']
    signals['short_mavg'] = data['Close'].rolling(window=short_window, min_periods=1, center=False).mean()
    signals['long_mavg'] = data['Close'].rolling(window=long_window, min_periods=1, center=False).mean()
    signals['signal'] = 0.0
    signals['signal'][short_window:] = (signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:]).astype(float)
    signals['positions'] = signals['signal'].diff()
    return signals

def update(frame):
    ax.clear()  # Clear only the axis instead of the entire figure
    new_data = get_stock_data(stock_symbol, interval='1m', hours_back=30)
    signals = simple_moving_average_strategy(new_data)

    # Convert date index to numbers for plotting
    new_data['Date_num'] = mpdates.date2num(new_data.index)
    ohlc = new_data[['Date_num', 'Open', 'High', 'Low', 'Close']].values

    candlestick_ohlc(ax, ohlc, width=0.0005, colorup='g', colordown='r', alpha=0.8)

    if not signals.empty:
        ax.plot(new_data.index, signals['short_mavg'], label='Short MA', linestyle='-')
        ax.plot(new_data.index, signals['long_mavg'], label='Long MA', linestyle='-')

        buy_indices = signals.loc[signals.positions == 1.0].index
        buy_values = new_data.loc[buy_indices]['Close']
        ax.scatter(buy_indices, buy_values, marker='^', color='g', label='Buy', alpha=1, s=100)

        sell_indices = signals.loc[signals.positions == -1.0].index
        sell_values = new_data.loc[sell_indices]['Close']
        ax.scatter(sell_indices, sell_values, marker='v', color='r', label='Sell', alpha=1, s=100)

        # profit/loss
        for index, row in signals.iterrows():
            if row['positions'] == 1.0:
                profit_loss = new_data.loc[index:, 'Close'].pct_change().sum()
                ax.text(index, new_data.loc[index, 'Close'], f'{profit_loss * 100:.2f}%', color='#27AE60', fontsize=10, ha='right')
            elif row['positions'] == -1.0:
                profit_loss = new_data.loc[index:, 'Close'].pct_change().sum()
                ax.text(index, new_data.loc[index, 'Close'], f'{profit_loss * 100:.2f}%', color='#ED4245', fontsize=10, ha='left')

    ax.set_title(f'{stock_symbol} - Real-Time Moving Average Strategy')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.legend()

stock_symbol = 'TSLA'

fig, ax = plt.subplots(figsize=(12, 8))
ani = FuncAnimation(fig, update, interval=1000, cache_frame_data=False)  # Added cache_frame_data=False
plt.show()  
