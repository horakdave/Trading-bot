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
    limit = 100  # historical data fetch pts
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit)
    return ohlcv

def is_shooting_star(candle):
    # Shooting star conditions:
    body_size = abs(candle[1] - candle[4])
    upper_shadow = max(candle[2], candle[3]) - candle[1]

    body_size_threshold = 0.1
    upper_shadow_threshold = 2

    return body_size <= body_size_threshold * candle[4] and upper_shadow >= upper_shadow_threshold * body_size

def calculate_trade_amount(current_capital, price, transaction_cost, factor=-0.005):
    max_trade_amount = current_capital * factor
    trade_amount = max_trade_amount / price
    transaction_fee = trade_amount * price * transaction_cost
    return trade_amount - transaction_fee

def trade_bitcoin(capital):
    percentage_change = 0.01  # 1%
    transaction_cost = 0.0005
    current_capital = capital
    bitcoin_amount = 0.0
    cumulative_gain_loss = 0.0
    current_gain_loss = 0.0
    hold = False

    historical_data = get_historical_data()

    for candle in historical_data:
        time.sleep(1)  #real-time behavior
        close_price = get_real_time_bitcoin_price()

        price_change = (close_price / historical_data[0][4] - 1) * 100

        shooting_star = is_shooting_star(candle)

        if hold:
            current_gain_loss = (close_price - historical_data[0][4]) * bitcoin_amount
            print(f"Current price:  {close_price} USD        Change: {price_change:.2f}%          Gain/Loss: {current_gain_loss:.2f} USD")

        if not hold and (price_change <= -percentage_change or shooting_star):
            hold = True
            bitcoin_amount_to_buy = calculate_trade_amount(current_capital, close_price, transaction_cost)
            bitcoin_amount += bitcoin_amount_to_buy
            usd_equivalent = bitcoin_amount_to_buy * close_price
            current_capital -= usd_equivalent
            print(f"Buy:            {usd_equivalent:.2f} BTC/USD     Change: {price_change:.2f}%          Gain/Loss: {current_gain_loss:.2f} USD")
            if shooting_star:
                print("SHOOTING STAR")
            

        elif hold and (price_change >= percentage_change or shooting_star):
            hold = False
            bitcoin_amount_to_sell = calculate_trade_amount(current_capital, close_price, transaction_cost)
            bitcoin_amount -= bitcoin_amount_to_sell
            usd_equivalent = bitcoin_amount_to_sell * close_price
            current_capital += usd_equivalent
            cumulative_gain_loss += current_gain_loss
            print(f"Sell:          {usd_equivalent:.2f} BTC/USD    Change: +{price_change:.2f}%         Gain/Loss: {current_gain_loss:.2f} USD")
            if shooting_star:
                print("SHOOTING STAR")


    print("Final Results:")
    total_change = ((current_capital + cumulative_gain_loss) / capital - 1) * 100
    print(f"Your bank acc.: {total_change:.2f} USD")

if __name__ == "__main__":
    starting_capital = 100
    trade_bitcoin(starting_capital)
