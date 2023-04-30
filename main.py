import os
from binance.client import Client
from dotenv import load_dotenv
import numpy as np
import time
from binance.exceptions import BinanceAPIException

# APIキーを読み込む
load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_SECRET_KEY")

# BinanceのAPIクライアントを生成する
client = Client(API_KEY, API_SECRET)

# 取引対象の仮想通貨
symbol = "BNBUSDT"

# 取引量
quantity = 0.001

# 移動平均線の期間
short_period = 20
long_period = 50


def get_price_data():
    # 過去の価格データを取得する
    klines = client.get_historical_klines(
        symbol, Client.KLINE_INTERVAL_1HOUR, "24 hour ago UTC"
    )

    # ローソク足の終値のみを取り出す
    close_prices = np.array([float(kline[4]) for kline in klines])

    # 現在の価格を取得する
    ticker = client.get_symbol_ticker(symbol=symbol)
    current_price = float(ticker["price"])

    return close_prices, current_price


def calc_moving_average(close_prices):
    # 移動平均線を計算する
    short_ma = np.mean(close_prices[-short_period:])
    long_ma = np.mean(close_prices[-long_period:])

    return short_ma, long_ma


def place_order(side, quantity, symbol, price=None):
    try:
        # Check if there's enough balance
        base_asset = symbol[:-4]  # Extract the base asset, e.g., BTC from BTCUSDT
        balance = client.get_asset_balance(asset=base_asset)
        available_balance = float(balance["free"])

        if side == "sell" and available_balance < quantity:
            print(f"Insufficient balance to place {side} order of {quantity} {symbol}.")
            return None
        if not price:
            ticker = client.get_symbol_ticker(symbol=symbol)
            current_price = float(ticker["price"])
        else:
            current_price = price

        order = client.create_order(
            symbol=symbol,
            side=side,
            type="LIMIT",
            timeInForce="GTC",
            quantity=quantity,
            price=current_price,
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


def main():
    while True:
        # 価格データを取得する
        close_prices, current_price = get_price_data()

        # 移動平均線を計算する
        short_ma, long_ma = calc_moving_average(close_prices)
        print(f"現在価格：{current_price}")
        print(f"短期移動平均線：{short_ma}")
        print(f"長期移動平均線：{long_ma}")

        # 売買条件を判断する
        if short_ma > long_ma:
            # 買い注文を出す
            order = place_order("buy", quantity, "BTCUSDT")
            print(f"買い注文を出しました：{order}")
        elif short_ma < long_ma:
            # 売り注文を出す
            order = place_order("sell", quantity, "BTCUSDT")
            print(f"売り注文を出しました：{order}")

        # 一定時間待機する
        time.sleep(60)


if __name__ == "__main__":
    main()
