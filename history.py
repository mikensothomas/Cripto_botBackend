from datetime import datetime

trade_history = []

def add_trade(action: str, price: float, quantity: float):
    trade_history.append({
        "action": action,
        "price": price,
        "quantity": quantity,
        "time": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })

def get_history():
    return trade_history[-50:]