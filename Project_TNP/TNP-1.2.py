import ccxt
import time

def get_real_time_bitcoin_price():
    exchange = ccxt.binance()
    symbol = 'BTC/USDT'
    ticker = exchange.fetch_ticker(symbol)
    return ticker['last']

def get_historical_data():
    exchange = ccxt.binance()
    symbol = 'BTC/USDT'
    timeframe = '1h'
    limit = 100  # historical data fetch points
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit)
    return ohlcv

def is_shooting_star(candle):
    # Shooting star conditions:
    body_size = abs(candle[1] - candle[4])
    upper_shadow = max(candle[2], candle[3]) - candle[1]

    body_size_threshold = 0.1
    upper_shadow_threshold = 2

    return body_size <= body_size_threshold * candle[4] and upper_shadow >= upper_shadow_threshold * body_size

def calculate_balance(current_balance, buy_price, sell_price, transaction_cost):
    # balance
    balance = current_balance * (1 - transaction_cost)
    return balance * (sell_price / buy_price)

def trade_bitcoin(capital):
    percentage_change = 0.01  # 1%
    shooting_star_threshold = -0.5
    transaction_cost = 0.0005
    current_capital = capital
    hold = False

    last_update_time = time.time()

    historical_data = get_historical_data()

    for candle in historical_data:
        time.sleep(1)  # Real time behavior
        close_price = get_real_time_bitcoin_price()

        price_change = (close_price / historical_data[0][4] - 1) * 100

        shooting_star = is_shooting_star(candle)

        if not hold and (price_change <= -percentage_change or shooting_star):
            hold = True
            current_capital = current_capital * (1 - transaction_cost)
            print(f"Buy: {close_price},     Change: {price_change:.2f}%,    Shooting Star: {shooting_star}")
        elif hold and (price_change >= percentage_change or shooting_star):
            hold = False
            current_capital = calculate_balance(current_capital, buy_price=close_price, sell_price=close_price, transaction_cost=transaction_cost)
            print(f"Sell: {close_price},    Change: +{price_change:.2f}%,  Shooting Star: {shooting_star}")
        else:
            print(f"On hold: {close_price},     Change: {price_change:.2f}%,    Shooting Star: {shooting_star}")

        current_time = time.time()
        if hold and current_time - last_update_time >= 30:
            print("")
            print(f"Your bank acc.: {current_capital:.2f} USD")
            print("")
            last_update_time = current_time

if __name__ == "__main__":
    starting_capital = 100
    trade_bitcoin(starting_capital)
