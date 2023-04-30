# Binance Automated Trading Bot

## Overview
このプログラムは、Binanceの仮想通貨取引所で自動取引を行うためのボットです。ボットは、移動平均線とボリンジャーバンドを使用して売買シグナルを生成し、条件に応じて買い注文または売り注文を出します。また、注文時にはストップロスとテイクプロフィットの設定も行います。

## Features
- 移動平均線に基づく売買シグナルの生成
- ボリンジャーバンドに基づく売買シグナルの生成
- ストップロスとテイクプロフィットの設定
- リスク管理に基づく注文の制限
- 取引チャートの描画

## How to Use
1. BinanceのAPIキーとシークレットキーを取得してください。
2. `.env`ファイルを作成し、以下の形式でAPIキーとシークレットキーを記入してください。
BINANCE_API_KEY=YOUR_API_KEY
BINANCE_SECRET_KEY=YOUR_SECRET_KEY

markdown
Copy code
3. 必要に応じて、プログラム内の以下の変数を変更してください。
symbol = "BNBUSDT" # 取引対象のペア
quantity = 0.1 # 取引量
short_period = 20 # 短期移動平均線の期間
long_period = 50 # 長期移動平均線の期間
stop_loss_pct = 0.01 # ストップロスの割合
take_profit_pct = 0.02 # テイクプロフィットの割合
risk_pct = 0.01 # リスク管理の割合

markdown
Copy code
4. プログラムを実行して、自動取引を開始してください。
python main.py

注: このプログラムはデモンストレーション用であり、実際の取引には十分なテストと検証が必要です。リスクを理解し、自己責任でご使用ください。