import ccxt
import time

def get_bitcoin_data():
    exchange = ccxt.binance()  # preferovany exchange(nevim co je)
    symbol = 'BTC/USD'  # trading pair
    ticker = exchange.fetch_ticker(symbol)
    return ticker['last']

def trade_bitcoin(capital):
    percentage_change = 0.001 #upravit
    threshold_high = 10
    threshold_low = -10
    transaction_cost = 0.0005
    current_capital = capital
    hold = False

    while True:
        price = get_bitcoin_data()
        if hold:
            new_capital = current_capital + current_capital * percentage_change
            if new_capital / current_capital > 1 + threshold_high * percentage_change:
                hold = False
                current_capital = new_capital * (1 - transaction_cost)
                print("Sell:", price)
        else:
            new_capital = current_capital - current_capital * percentage_change
            if new_capital / current_capital < 1 + threshold_low * percentage_change:
                hold = True
                current_capital = new_capital * (1 - transaction_cost)
                print("Buy:", price)

        print("on hold:", price)
        time.sleep(1)

if __name__ == "__main__":
    starting_capital = 100
    trade_bitcoin(starting_capital)