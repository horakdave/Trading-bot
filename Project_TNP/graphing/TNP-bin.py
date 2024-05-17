import numpy as np
from binance.client import Client
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime, timedelta
import pyttsx3

client = Client()
engine = pyttsx3.init()

def get_crypto_data(symbol, interval='1m', hours_back=30):
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(hours=hours_back)
    klines = client.get_historical_klines(symbol, interval, start_date.strftime("%d %b %Y %H:%M:%S"), end_date.strftime("%d %b %Y %H:%M:%S"))
    data = pd.DataFrame(klines, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
    data['Close'] = pd.to_numeric(data['Close'])
    data.index = pd.to_datetime(data['Open time'], unit='ms')
    return data

def simple_moving_average_strategy(data, short_window=10, long_window=50):
    signals = pd.DataFrame(index=data.index)
    signals['price'] = data['Close']
    signals['short_mavg'] = data['Close'].rolling(window=short_window, min_periods=1).mean()
    signals['long_mavg'] = data['Close'].rolling(window=long_window, min_periods=1).mean()
    signals['signal'] = 0.0
    signals['signal'][short_window:] = np.where(signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1.0, 0.0)
    signals['positions'] = signals['signal'].diff()
    return signals

last_position = 0

def update(frame):
    global last_position
    new_data = get_crypto_data('BTCUSDT', interval='1m', hours_back=30)
    signals = simple_moving_average_strategy(new_data)

    plt.clf()
    plt.plot(new_data.index, new_data['Close'], label='BTC Price')
    plt.plot(signals.index, signals['short_mavg'], label='Short MA')
    plt.plot(signals.index, signals['long_mavg'], label='Long MA')

    # Checkovani a zaroven logovani novych signalu
    current_position = signals['positions'].iloc[-1]
    if current_position == 1.0 and last_position != 1.0:
        print(f"Buy signal at {signals.index[-1]}")
        engine.say("Buy signal detected.")
        engine.runAndWait()
    elif current_position == -1.0 and last_position != -1.0:
        print(f"Sell signal at {signals.index[-1]}")
        engine.say("Sell signal detected.")
        engine.runAndWait()
    
    last_position = current_position

    plt.scatter(signals.loc[signals.positions == 1.0].index, signals.loc[signals.positions == 1.0, 'short_mavg'], marker='^', color='g', label='Buy', s=100)
    plt.scatter(signals.loc[signals.positions == -1.0].index, signals.loc[signals.positions == -1.0, 'short_mavg'], marker='v', color='r', label='Sell', s=100)
    plt.title('BTCUSDT - Real-Time Moving Average Strategy')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    

fig, ax = plt.subplots(figsize=(12, 8))
ani = FuncAnimation(fig, update, interval=120000)
plt.show()
