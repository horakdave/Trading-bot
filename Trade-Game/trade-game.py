import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from datetime import datetime
from binance.client import Client
from matplotlib.animation import FuncAnimation

initial_capital = 0
crypto_symbol = 'BTCUSDT'
client = Client()

print("Welcome to THE TRADE GAME")
print("You start with 1 bitcoin.")
print("The goal is to make a lot of money by trading the bitcoin.")
print("You can use binance, delta or any other crypto site to improve your experience")
print("Good luck!")
print("--------------------------------------------------")

def get_crypto_data(symbol, interval='1m'):
    return client.get_historical_klines(symbol, interval, "1 day ago UTC")

fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.3)

def is_market_open():
    return True

def update(val):
    ax.clear()
    if is_market_open():
        data = pd.DataFrame(get_crypto_data(crypto_symbol), columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
        data['Close'] = pd.to_numeric(data['Close'])
        data.index = pd.to_datetime(data['Open time'], unit='ms')
        ax.plot(data.index, data['Close'])
        ax.set_title(f'{crypto_symbol} Price')
        ax.set_xlabel('Time')
        ax.set_ylabel('Price')
    else:
        ax.text(0.5, 0.5, 'Market Closed', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
    plt.draw()

def buy_crypto(event):
    global initial_capital
    if is_market_open():
        data = pd.DataFrame(get_crypto_data(crypto_symbol), columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
        data['Close'] = pd.to_numeric(data['Close'])
        last_price = data['Close'].iloc[-1]
        if initial_capital >= last_price:
            initial_capital -= last_price
            bitcoins_held = 1
            print(f"Bought at {last_price}, new balance: {initial_capital}")
            with open("save1.txt", "w") as file:
                file.write(f"Current balance: {initial_capital}\nBitcoins held: {bitcoins_held}\n")
        else:
            print("Not enough money to buy.")
    else:
        print("Market is closed, cannot buy.")

def sell_crypto(event):
    global initial_capital
    if is_market_open():
        data = pd.DataFrame(get_crypto_data(crypto_symbol), columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
        data['Close'] = pd.to_numeric(data['Close'])
        last_price = data['Close'].iloc[-1]
        with open("save1.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                if "Bitcoins held" in line:
                    bitcoins_held = int(line.split(":")[1].strip())
                    break
        if bitcoins_held >= 1:
            initial_capital += last_price
            bitcoins_held -= 1
            print(f"Sold at {last_price}, new balance: {initial_capital}")
            with open("save1.txt", "w") as file:
                file.write(f"Current balance: {initial_capital}\nBitcoins held: {bitcoins_held}\n")
        else:
            print("Not enough bitcoins to sell.")
    else:
        print("Market is closed, cannot sell.")

update_button_ax = plt.axes([0.7, 0.05, 0.1, 0.075])
update_button = Button(update_button_ax, 'Update', color='lightgoldenrodyellow', hovercolor='0.975')
update_button.on_clicked(update)

buy_button_ax = plt.axes([0.1, 0.05, 0.1, 0.075])
buy_button = Button(buy_button_ax, 'Buy', color='lightgreen', hovercolor='0.975')
buy_button.on_clicked(buy_crypto)

sell_button_ax = plt.axes([0.3, 0.05, 0.1, 0.075])
sell_button = Button(sell_button_ax, 'Sell', color='lightcoral', hovercolor='0.975')
sell_button.on_clicked(sell_crypto)

ani = FuncAnimation(fig, update, interval=120000, cache_frame_data=False)  #2 min

if is_market_open():
    initial_data = pd.DataFrame(get_crypto_data(crypto_symbol), columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
    initial_data['Close'] = pd.to_numeric(initial_data['Close'])
    initial_data.index = pd.to_datetime(initial_data['Open time'], unit='ms')
    ax.plot(initial_data.index, initial_data['Close'])
    ax.set_title(f'{crypto_symbol} Price')
    ax.set_xlabel('Time')
    ax.set_ylabel('Price')

plt.show()
