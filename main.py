import os
from binance.client import Client
from dotenv import load_dotenv
import numpy as np
import time
from binance.exceptions import BinanceAPIException
import pandas as pd
import matplotlib.pyplot as plt

# APIキーを読み込む
load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_SECRET_KEY")

# BinanceのAPIクライアントを生成する
client = Client(API_KEY, API_SECRET)

# 取引対象の仮想通貨
symbol = "BNBUSDT"
base_asset = "BNB"
quote_asset = "USDT"
quantity = 0.1
short_period = 20
long_period = 50
stop_loss_pct = 0.01
take_profit_pct = 0.02
risk_pct = 0.01


def get_price_data():
    # 過去の価格データを取得する（過去50時間分のデータ）
    klines = client.get_historical_klines(
        symbol, Client.KLINE_INTERVAL_1HOUR, "50 hours ago UTC"
    )
    close_prices = np.array([float(kline[4]) for kline in klines])
    ticker = client.get_symbol_ticker(symbol=symbol)
    current_price = float(ticker["price"])
    return close_prices, current_price


def calc_moving_average(close_prices):
    short_ma = np.mean(close_prices[-short_period:])
    long_ma = np.mean(close_prices[-long_period:])
    return short_ma, long_ma


def calc_bollinger_bands(close_prices, window=20, multiplier=2):
    sma = np.mean(close_prices[-window:])
    std = np.std(close_prices[-window:])
    upper_band = sma + (multiplier * std)
    lower_band = sma - (multiplier * std)
    return sma, upper_band, lower_band


def place_order(side, quantity, symbol, stop_loss_pct, take_profit_pct):
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        current_price = float(ticker["price"])
        if side == "buy":
            stop_loss = current_price * (1 - stop_loss_pct)
            take_profit = current_price * (1 + take_profit_pct)
        else:
            stop_loss = current_price * (1 + stop_loss_pct)
            take_profit = current_price * (1 - take_profit_pct)
        if abs(current_price - stop_loss) / current_price > risk_pct:
            print("Risk limit exceeded. Order not placed.")
            return None
        order = client.create_order(
            symbol=symbol,
            side=side,
            type=Client.ORDER_TYPE_LIMIT,
            timeInForce=Client.TIME_IN_FORCE_GTC,
            quantity=quantity,
            price=current_price,
            stopPrice=stop_loss,
            stopLimitPrice=take_profit,
            stopLimitTimeInForce=Client.TIME_IN_FORCE_GTC,
        )
        print(
            f"{side.capitalize()} order of {quantity} {symbol} at {current_price:.2f} placed."
        )
        return order
    except BinanceAPIException as e:
        print(
            f"Failed to place {side} order of {quantity} {symbol} at {current_price:.2f}. Error message: {e}"
        )
        return None


def plot_chart(
    close_prices, short_ma, long_ma, upper_band, lower_band, buy_signals, sell_signals
):
    data = pd.DataFrame()
    data["Close"] = close_prices
    data["Short_MA"] = short_ma
    data["Long_MA"] = long_ma
    data["Upper_Band"] = upper_band
    data["Lower_Band"] = lower_band
    data["Buy_Signal"] = buy_signals
    data["Sell_Signal"] = sell_signals

    plt.figure(figsize=(12, 6))
    plt.plot(data["Close"], label="Close", color="black", alpha=0.3)
    plt.plot(data["Short_MA"], label="Short MA", color="blue", alpha=0.7)
    plt.plot(data["Long_MA"], label="Long MA", color="red", alpha=0.7)
    plt.plot(data["Upper_Band"], label="Upper Band", color="green", alpha=0.7)
    plt.plot(data["Lower_Band"], label="Lower Band", color="orange", alpha=0.7)
    plt.scatter(
        data.index,
        data["Buy_Signal"],
        label="Buy Signal",
        marker="^",
        color="green",
        alpha=1,
    )
    plt.scatter(
        data.index,
        data["Sell_Signal"],
        label="Sell Signal",
        marker="v",
        color="red",
        alpha=1,
    )
    plt.title("Price Chart with Moving Averages and Bollinger Bands")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend(loc="upper left")
    plt.show()


def main():
    close_prices, current_price = get_price_data()
    buy_signals = [None] * len(close_prices)
    sell_signals = [None] * len(close_prices)

    while True:
        close_prices, current_price = get_price_data()
        print(f"Current price: {current_price:.2f}")
        short_ma, long_ma = calc_moving_average(close_prices)
        print(f"Short MA: {short_ma:.2f}")
        sma, upper_band, lower_band = calc_bollinger_bands(close_prices)
        print(f"Upper band: {upper_band:.2f}")

        if short_ma > long_ma and current_price > lower_band:
            print("Buy signal")
            order = place_order("buy", quantity, symbol, stop_loss_pct, take_profit_pct)
            print(order)
            buy_signals[-1] = current_price
            print(buy_signals[-1])
        elif short_ma < long_ma and current_price < upper_band:
            print("Sell signal")
            order = place_order(
                "sell", quantity, symbol, stop_loss_pct, take_profit_pct
            )
            print(order)
            sell_signals[-1] = current_price
            print(sell_signals[-1])
        plot_chart(
            close_prices,
            short_ma,
            long_ma,
            upper_band,
            lower_band,
            buy_signals,
            sell_signals,
        )
        time.sleep(5)


if __name__ == "__main__":
    main()
