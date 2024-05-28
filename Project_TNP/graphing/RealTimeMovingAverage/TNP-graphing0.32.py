import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.dates as mdates
from datetime import datetime, timedelta

plt.style.use('dark_background')

def get_stock_data(symbol, interval='1m', hours_back=24):   # adjustable
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=hours_back) - timedelta(hours=14)
    return yf.download(symbol, interval=interval, start=start_date, end=end_date)

def simple_moving_average_strategy(data, short_window=10, long_window=50):
    signals = pd.DataFrame(index=data.index)
    signals['price'] = data['Close']
    signals['short_mavg'] = data['Close'].rolling(window=short_window, min_periods=1, center=False).mean()
    signals['long_mavg'] = data['Close'].rolling(window=long_window, min_periods=1, center=False).mean()
    signals['signal'] = 0.0
    signals['signal'][short_window:] = (signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:]).astype(float)
    signals['positions'] = signals['signal'].diff()
    return signals

def update(frame):
    new_data = get_stock_data(stock_symbol, interval='1m', hours_back=30)
    signals = simple_moving_average_strategy(new_data)

    plt.style.use('dark_background')

    plt.rcParams['grid.color'] = '#3A3B3C'
    plt.rcParams['axes.labelcolor'] = '#99AAB5'
    plt.rcParams['xtick.color'] = '#99AAB5'
    plt.rcParams['ytick.color'] = '#99AAB5'
    plt.rcParams['lines.color'] = '#5865F2'

    plt.clf()

    plt.plot(new_data['Close'], color='#5865F2', label=f'{stock_symbol} Price')

    if not signals.empty:
        plt.plot(signals['short_mavg'], label='Short MA', linestyle='-', linewidth=2, color='#F4C20D')
        plt.plot(signals['long_mavg'], label='Long MA', linestyle='-', linewidth=2, color='#ED4245')

        buy_indices = signals.loc[signals.positions == 1.0].index
        buy_values = new_data.loc[buy_indices]['Close']
        plt.scatter(buy_indices, buy_values, marker='^', color='#27AE60', label='Buy', alpha=1, s=100)

        sell_indices = signals.loc[signals.positions == -1.0].index
        sell_values = new_data.loc[sell_indices]['Close']
        plt.scatter(sell_indices, sell_values, marker='v', color='#ED4245', label='Sell', alpha=1, s=100)

        # profit/loss
        for index, row in signals.iterrows():
            if row['positions'] == 1.0:
                profit_loss = new_data.loc[index:, 'Close'].pct_change().sum()
                plt.text(index, new_data.loc[index, 'Close'], f'{profit_loss * 100:.2f}%', color='#27AE60', fontsize=10, ha='right')
            elif row['positions'] == -1.0:
                profit_loss = new_data.loc[index:, 'Close'].pct_change().sum()
                plt.text(index, new_data.loc[index, 'Close'], f'{profit_loss * 100:.2f}%', color='#ED4245', fontsize=10, ha='left')

    plt.title(f'{stock_symbol} - Real-Time Moving Average Strategy')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()

    plt.grid(b=True, which='major', color='#3A3B3C', linestyle='-', linewidth=1)
    plt.grid(b=True, which='minor', color='#3A3B3C', linestyle='-', linewidth=0.5)

    plt.ylim(top=new_data['Close'].max() * 1.05, bottom=new_data['Close'].min() * 0.95)
    plt.xlim(left=new_data.index[0], right=new_data.index[-1])

    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
    plt.gca().xaxis.set_minor_locator(mdates.MinuteLocator(interval=5))


stock_symbol = 'TSLA' # chose your own stock

fig, ax = plt.subplots(figsize=(12, 8))
ax.set_facecolor('#2C2F33')
ani = FuncAnimation(fig, update, interval=60000) #adjustable (keep 000)
plt.show()
