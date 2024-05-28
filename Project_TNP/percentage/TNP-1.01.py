import ccxt
import time

def get_bitcoin_data():
    exchange = ccxt.binance()
    symbol = 'BTC/USDT'
    ticker = exchange.fetch_ticker(symbol)
    return ticker['last']



def calculate_trade_amount(current_capital, price, transaction_cost, factor=-0.005):
    max_trade_amount = current_capital * factor
    trade_amount = max_trade_amount / price
    transaction_fee = trade_amount * price * transaction_cost
    return trade_amount - transaction_fee

def trade_bitcoin(capital):
    percentage_change = 0.01 # 1%
    transaction_cost = 0.0005
    current_capital = capital
    bitcoin_amount = 0.0
    cumulative_gain_loss = 0.0
    hold = False

    previous_price = get_bitcoin_data()

    start_time = time.time()
    interval = 60

    while True:
        time.sleep(1)
        elapsed_time = time.time() - start_time

        if elapsed_time >= interval:
            start_time = time.time()
            total_change = ((current_capital + cumulative_gain_loss) / capital - 1) * 100
            print("-----------------------------------------------------------")
            print(f"your bank acc.: {total_change:.2f} USD")
            print("-----------------------------------------------------------")

        price = get_bitcoin_data()
        price_change = (price / previous_price - 1) * 100

        if hold:
            current_gain_loss = (price - previous_price) * bitcoin_amount
            print(f"Current price: {price} USD        Change: {price_change:.2f}%          Gain/Loss: {current_gain_loss:.2f} USD")

        if not hold and price_change <= -percentage_change:
            hold = True
            bitcoin_amount_to_buy = calculate_trade_amount(current_capital, price, transaction_cost)
            bitcoin_amount += bitcoin_amount_to_buy
            usd_equivalent = bitcoin_amount_to_buy * price
            current_capital -= usd_equivalent
            print(f"Buy:            {usd_equivalent:.2f} BTC/USD     Change: {price_change:.2f}%")

        elif hold and price_change >= percentage_change:
            hold = False
            bitcoin_amount_to_sell = calculate_trade_amount(current_capital, price, transaction_cost)
            bitcoin_amount -= bitcoin_amount_to_sell
            usd_equivalent = bitcoin_amount_to_sell * price
            current_capital += usd_equivalent
            cumulative_gain_loss += current_gain_loss
            print(f"Sell:          {usd_equivalent:.2f} BTC/USD    Change: +{price_change:.2f}%         Gain/Loss: {current_gain_loss:.2f} USD")

        previous_price = price

if __name__ == "__main__":
    starting_capital = 100
    trade_bitcoin(starting_capital)