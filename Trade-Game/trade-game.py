import tkinter as tk
from tkinter import Button
from binance.client import Client
import pandas as pd

initial_capital = 0
crypto_symbol = 'BTCUSDT'
client = Client()

print("Welcome to THE TRADE GAME")
print("You start with 1 bitcoin.")
print("The goal is to make a lot of money by trading the bitcoin.")
print("You can use binance, delta or any other crypto site to improve your experience")
print("Good luck!")
print("--------------------------------------------------")

def is_market_open():
    return True

def get_crypto_data(symbol, interval='1m'):
    return client.get_historical_klines(symbol, interval, "1 day ago UTC")

def buy_crypto():
    global initial_capital
    if is_market_open():
        data = pd.DataFrame(get_crypto_data(crypto_symbol), columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
        last_price = pd.to_numeric(data['Close'].iloc[-1])
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

def sell_crypto():
    global initial_capital
    if is_market_open():
        data = pd.DataFrame(get_crypto_data(crypto_symbol), columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
        last_price = pd.to_numeric(data['Close'].iloc[-1])
        with open("save1.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                if "Bitcoins held" in line:
                    bitcoins_held = int(line.split(":")[1].strip())
                    break
        if bitcoins_held >= 1:
            sell_amount = last_price * 0.98  # 2% sell fee
            initial_capital += sell_amount
            bitcoins_held -= 1
            print(f"your sell fee is {sell_amount} (2%)")
            print(f"Sold at {last_price}, new balance: {initial_capital}")
            with open("save1.txt", "w") as file:
                file.write(f"Current balance: {initial_capital}\nBitcoins held: {bitcoins_held}\n")
        else:
            print("Not enough bitcoins to sell.")
    else:
        print("Market is closed, cannot sell.")

root = tk.Tk()
root.title("Crypto Trading Game")

buy_button = Button(root, text="Buy", command=buy_crypto, bg='lightgreen', height=10, width=35)
buy_button.pack(side=tk.LEFT)

sell_button = Button(root, text="Sell", command=sell_crypto, bg='lightcoral', height=10, width=35)
sell_button.pack(side=tk.LEFT)

root.mainloop()