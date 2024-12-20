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
    
    # Add columns to track buy prices
    signals['buy_price_1'] = 0.0
    signals['buy_price_2'] = 0.0
    signals['buy_price_3'] = 0.0
    
    # Track buy prices when positions change to 1
    buy_indices_1 = signals.index[signals['positions_1'] == 1.0]
    buy_indices_2 = signals.index[signals['positions_2'] == 1.0]
    buy_indices_3 = signals.index[signals['positions_3'] == 1.0]
    
    signals.loc[buy_indices_1, 'buy_price_1'] = data.loc[buy_indices_1, 'Close']
    signals.loc[buy_indices_2, 'buy_price_2'] = data.loc[buy_indices_2, 'Close']
    signals.loc[buy_indices_3, 'buy_price_3'] = data.loc[buy_indices_3, 'Close']
    
    return signals

def update(frame):
    new_data = get_stock_data(stock_symbol, interval='1m', hours_back=30)
    signals = simple_moving_average_strategy(new_data)

    plt.clf()

    # Plot the price and moving averages
    plt.plot(new_data['Close'], label=f'{stock_symbol} Price')
    plt.plot(signals['ma_1'], label='MA (5)', linestyle='-')
    plt.plot(signals['ma_2'], label='MA (10)', linestyle='-')
    plt.plot(signals['ma_3'], label='MA (20)', linestyle='-', alpha=0.7)

    if not signals.empty:
        # MA1 signals and profit/loss
        buy_indices = signals.loc[signals.positions_1 == 1.0].index
        buy_values = new_data.loc[buy_indices]['Close']
        plt.scatter(buy_indices, buy_values, marker='^', color='#90EE90', label='Buy MA1', alpha=1, s=60)

        sell_indices = signals.loc[signals.positions_1 == -1.0].index
        sell_values = new_data.loc[sell_indices]['Close']
        plt.scatter(sell_indices, sell_values, marker='v', color='#FFB6C1', label='Sell MA1', alpha=1, s=60)

        # Calculate and display profit/loss for MA1
        for buy_idx, sell_idx in zip(buy_indices, sell_indices):
            if buy_idx < sell_idx:  # Only calculate if buy comes before sell
                buy_price = new_data.loc[buy_idx, 'Close']
                sell_price = new_data.loc[sell_idx, 'Close']
                profit_pct = ((sell_price - buy_price) / buy_price) * 100
                color = '#27AE60' if profit_pct >= 0 else '#ED4245'
                plt.text(sell_idx, sell_price, f'{profit_pct:.2f}%', 
                        color=color, fontsize=14, weight='bold',
                        ha='left', va='bottom')

        # MA2 signals
        buy_indices = signals.loc[signals.positions_2 == 1.0].index
        buy_values = new_data.loc[buy_indices]['Close']
        plt.scatter(buy_indices, buy_values, marker='^', color='#32CD32', label='Buy MA2', alpha=0.8, s=120)

        sell_indices = signals.loc[signals.positions_2 == -1.0].index
        sell_values = new_data.loc[sell_indices]['Close']
        plt.scatter(sell_indices, sell_values, marker='v', color='#DC143C', label='Sell MA2', alpha=0.8, s=120)

        # MA3 signals
        buy_indices = signals.loc[signals.positions_3 == 1.0].index
        buy_values = new_data.loc[buy_indices]['Close']
        plt.scatter(buy_indices, buy_values, marker='^', color='#006400', label='Buy MA3', alpha=0.6, s=180)

        sell_indices = signals.loc[signals.positions_3 == -1.0].index
        sell_values = new_data.loc[sell_indices]['Close']
        plt.scatter(sell_indices, sell_values, marker='v', color='#8B0000', label='Sell MA3', alpha=0.6, s=180)

    plt.title(f'{stock_symbol} - Real-Time Moving Average Strategy')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()

stock_symbol = 'TSLA'

fig, ax = plt.subplots(figsize=(14, 8))
ani = FuncAnimation(fig, update, interval=120000) #adjustable (120sec)
plt.show()
