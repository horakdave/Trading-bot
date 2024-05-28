import ccxt
import time

def get_bitcoin_data():
    exchange = ccxt.binance()
    symbol = 'BTC/USDT'
    ticker = exchange.fetch_ticker(symbol)
    return ticker['last']

def trade_bitcoin(capital):
    percentage_change = 0.01  # 1%
    transaction_cost = 0.0005
    current_capital = capital
    hold = False

    previous_price = get_bitcoin_data()

    start_time = time.time()
    interval = 60

    while True:
        time.sleep(1)
        elapsed_time = time.time() - start_time

        if elapsed_time >= interval:
            start_time = time.time()
            total_change = ((current_capital / capital) - 1) * 100
            print(f"Total Change: {total_change:.2f}%")
        
        price = get_bitcoin_data()
        price_change = (price / previous_price - 1) * 100

        if not hold and price_change <= -percentage_change:
            hold = True
            current_capital = current_capital * (1 - transaction_cost)
            print(f"Buy: {price}       Change: {price_change:.2f}%")
        elif hold and price_change >= percentage_change:
            hold = False
            current_capital = current_capital * (1 - transaction_cost)
            print(f"Sell: {price}      Change: +{price_change:.2f}%")
        else:
            print(f"On hold: {price}       Change: {price_change:.2f}%")

        previous_price = price

if __name__ == "__main__":
    starting_capital = 100
    trade_bitcoin(starting_capital)
