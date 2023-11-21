import ccxt
import time

def get_bitcoin_data():
    exchange = ccxt.binance()
    symbol = 'BTC/USDT'
    ticker = exchange.fetch_ticker(symbol)
    return ticker['last']

def calculate_trade_amount(current_capital, price, transaction_cost, factor= -0.005): # upravit factor
    max_trade_amount = current_capital * factor
    trade_amount = max_trade_amount / price
    transaction_fee = trade_amount * price * transaction_cost
    return trade_amount - transaction_fee

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
            print("-----------------------------------------------------------")
            print(f"Total Change: {total_change:.2f} USD")
            print("-----------------------------------------------------------")
        
        price = get_bitcoin_data()
        price_change = (price / previous_price - 1) * 100

        if not hold and price_change <= -percentage_change:
            hold = True
            bitcoin_amount_to_buy = calculate_trade_amount(current_capital, price, transaction_cost)
            usd_equivalent = bitcoin_amount_to_buy * price
            current_capital -= usd_equivalent
            gain_loss = current_capital - capital   #gain_loss je udelanej spatne
            print(f"Buy: {usd_equivalent:.2f} USD     Change: {price_change:.2f}%          Gain/Loss: {gain_loss:.2f} USD") #gain_loss je udelanej spatne

        elif hold and price_change >= percentage_change:
            if total_change == 0:   #hold = False
                hold = False
            bitcoin_amount_to_sell = calculate_trade_amount(current_capital, price, transaction_cost)
            usd_equivalent = bitcoin_amount_to_sell * price
            current_capital += usd_equivalent
            gain_loss = current_capital - capital   #gain_loss je udelanej spatne
            print(f"Sell: {usd_equivalent:.2f} BTC/USD    Change: +{price_change:.2f}%         Gain/Loss: {gain_loss:.2f} USD")
        
        else:
            print(f"On hold: {price} USD        Change: {price_change:.2f}%")

        previous_price = price

if __name__ == "__main__":
    starting_capital = 100
    trade_bitcoin(starting_capital)
