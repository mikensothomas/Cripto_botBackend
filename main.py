from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import threading
import bot
from bot import get_balance
from history import get_history
import asyncio
from binance.client import Client
from dotenv import load_dotenv
import os
import uvicorn

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(API_KEY, API_SECRET)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

bot_thread = None

@app.get("/")
def home():
    return {"status": "API Binance Bot ativa."}

@app.post("/start")
def start_bot():
    global bot_thread

    if bot.bot_running:
        return {"message": "Bot já está rodando"}

    bot_thread = threading.Thread(target=bot.run_bot)
    bot_thread.start()

    return {"message": "Bot iniciado"}

@app.post("/stop")
def stop_bot():
    bot.stop_bot()
    return {"message": "Bot parado"}

@app.get("/status")
def get_status():
    return {
        "running": bot.bot_running,
        "data": bot.last_status
    }

@app.get("/balance")
def get_balances():
    brl = get_balance("BRL")
    btc = get_balance("BTC")

    return {
        "BRL": brl,
        "BTC": btc
    }

@app.get("/history")
def history():
    return get_history()

@app.websocket("/ws/btc")
async def btc_price(ws: WebSocket):
    await ws.accept()

    while True:
        price = client.get_symbol_ticker(symbol="BTCUSDT")
        await ws.send_json({
            "price": float(price["price"])
        })
        await asyncio.sleep(1)
