from dotenv import load_dotenv
import os
import time
import threading
from binance.client import Client
from history import add_trade

load_dotenv()

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_SECRET_KEY")

client = Client(api_key, api_secret)

symbol = "BTCBRL"
currency_btc = "BTC"
currency_brl = "BRL"

percentage_to_buy = 1
percentage_to_sell = 2
TAKE_PROFIT = 1.05
STOP_LOSS = 0.97


bot_running = False
last_status = {}
stop_event = threading.Event()

def get_balance(currency):
    account = client.get_account()
    for asset in account["balances"]:
        if asset["asset"] == currency:
            return float(asset["free"])
    return 0.0

def get_balance(asset):
    account = client.get_account()
    for b in account["balances"]:
        if b["asset"] == asset:
            return float(b["free"])
    return 0.0

def get_price(symbol: str) -> float:
    ticker = client.get_symbol_ticker(symbol=symbol)
    return float(ticker["price"])

def buy():
    brl_balance = get_balance("BRL")

    if brl_balance < 20:
        raise Exception("Saldo em BRL insuficiente para comprar")

    value_to_buy = brl_balance * 0.4

    order = client.create_order(
        symbol="BTCBRL",
        side="BUY",
        type="MARKET",
        quoteOrderQty=round(value_to_buy, 2)
    )
    add_trade("BUY", get_price("BTCBRL"), value_to_buy)
    return order

def sell():
    btc_balance = get_balance("BTC")

    if btc_balance < 0.00001:
        raise Exception("Saldo BTC insuficiente para venda")

    order = client.create_order(
        symbol="BTCBRL",
        side="SELL",
        type="MARKET",
        quantity=round(btc_balance, 6)
    )
    add_trade("SELL", get_price("BTCBRL"), btc_balance)
    return order

def run_bot():
    global bot_running, last_status
    stop_event.clear()
    bot_running = True
    entry_price = None

    while not stop_event.is_set():
        try:
            price = get_price("BTCBRL")

            if entry_price is None:
                buy()
                entry_price = price
                last_status = {
                    "action": "BUY",
                    "price": price
                }

            else:
                if price >= entry_price * TAKE_PROFIT:
                    sell()
                    last_status = {
                        "action": "SELL (TAKE PROFIT)",
                        "entry": entry_price,
                        "exit": price
                    }
                    entry_price = None
                elif price <= entry_price * STOP_LOSS:
                    sell()
                    last_status = {
                        "action": "SELL (STOP LOSS)",
                        "entry": entry_price,
                        "exit": price
                    }
                    entry_price = None

            time.sleep(5)

        except Exception as e:
            last_status = {"error": str(e)}
            time.sleep(5)

    bot_running = False
    last_status = {"status": "Bot parado"}

def stop_bot():
    stop_event.set()

