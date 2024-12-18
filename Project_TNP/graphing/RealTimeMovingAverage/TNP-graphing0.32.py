import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime, timedelta

def get_stock_data(symbol, interval='1m', hours_back=24):   # adjustable
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=hours_back) - timedelta(hours=0) # adjustable
    return yf.download(symbol, interval=interval, start=start_date, end=end_date)


def simple_moving_average_strategy(data, ma_1=5, ma_2=10, ma_3=20):
    signals = pd.DataFrame(index=data.index)
    signals['price'] = data['Close']
    signals['ma_1'] = data['Close'].rolling(window=ma_1, min_periods=1, center=False).mean()
    signals['ma_2'] = data['Close'].rolling(window=ma_2, min_periods=1, center=False).mean()
    signals['ma_3'] = data['Close'].rolling(window=ma_3, min_periods=1, center=False).mean()
    
    # Generate signals for each MA crossover
    signals['signal_1'] = 0.0
    signals['signal_2'] = 0.0
    signals['signal_3'] = 0.0
    
    # Using MA1 as the fastest MA, generate signals when it crosses the others
    signals['signal_1'][ma_1:] = (signals['ma_1'][ma_1:] > signals['ma_2'][ma_1:]).astype(float)
    signals['signal_2'][ma_1:] = (signals['ma_1'][ma_1:] > signals['ma_3'][ma_1:]).astype(float)
    signals['signal_3'][ma_1:] = (signals['ma_2'][ma_1:] > signals['ma_3'][ma_1:]).astype(float)
    
    signals['positions_1'] = signals['signal_1'].diff()
    signals['positions_2'] = signals['signal_2'].diff()
    signals['positions_3'] = signals['signal_3'].diff()
    
    return signals

def update(frame):
    new_data = get_stock_data(stock_symbol, interval='1m', hours_back=30)
    signals = simple_moving_average_strategy(new_data)

    plt.clf()

    plt.plot(new_data['Close'], label=f'{stock_symbol} Price')

    if not signals.empty:
        plt.plot(signals['ma_1'], label='MA (5)', linestyle='-')
        plt.plot(signals['ma_2'], label='MA (10)', linestyle='-')
        plt.plot(signals['ma_3'], label='MA (20)', linestyle='-', alpha=0.7)

        # MA1 signals (5 MA - smallest and lightest color)
        buy_indices = signals.loc[signals.positions_1 == 1.0].index
        buy_values = new_data.loc[buy_indices]['Close']
        plt.scatter(buy_indices, buy_values, marker='^', color='#90EE90', label='Buy MA1', alpha=1, s=60)  # Light green, small

        sell_indices = signals.loc[signals.positions_1 == -1.0].index
        sell_values = new_data.loc[sell_indices]['Close']
        plt.scatter(sell_indices, sell_values, marker='v', color='#FFB6C1', label='Sell MA1', alpha=1, s=60)  # Light red, small

        # MA2 signals (10 MA - medium size and color)
        buy_indices = signals.loc[signals.positions_2 == 1.0].index
        buy_values = new_data.loc[buy_indices]['Close']
        plt.scatter(buy_indices, buy_values, marker='^', color='#32CD32', label='Buy MA2', alpha=0.8, s=120)  # Medium green, medium

        sell_indices = signals.loc[signals.positions_2 == -1.0].index
        sell_values = new_data.loc[sell_indices]['Close']
        plt.scatter(sell_indices, sell_values, marker='v', color='#DC143C', label='Sell MA2', alpha=0.8, s=120)  # Medium red, medium


        # Profit/loss calculations (keeping just for MA1 to avoid clutter)
        for index, row in signals.iterrows():
            if row['positions_1'] == 1.0:
                profit_loss = new_data.loc[index:, 'Close'].pct_change().sum()
                plt.text(index, new_data.loc[index, 'Close'], f'{profit_loss * 100:.2f}%', color='#27AE60', fontsize=10, ha='right')
            elif row['positions_1'] == -1.0:
                profit_loss = new_data.loc[index:, 'Close'].pct_change().sum()
                plt.text(index, new_data.loc[index, 'Close'], f'{profit_loss * 100:.2f}%', color='#ED4245', fontsize=10, ha='left')

    plt.title(f'{stock_symbol} - Real-Time Moving Average Strategy')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()

stock_symbol = 'TSLA'

fig, ax = plt.subplots(figsize=(14, 8))
ani = FuncAnimation(fig, update, interval=120000) #adjustable (120sec)
plt.show()
