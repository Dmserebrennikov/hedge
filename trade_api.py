import requests
import json


URL = "http://127.0.0.1:8080"


def new_position(symbol, volume, side):
    endpoint = URL + "/new_position/"
    params = {
        "symbol": symbol,
        "volume": volume,
        "side": side
    }
    resp = requests.get(endpoint, json=params)
    if not resp.ok:
        raise ConnectionError(f"Something went wrong with the trade {symbol}")


def all_positions():
    endpoint = URL + "/all_positions/"
    resp = requests.get(endpoint)
    trades_info = json.loads(resp.json())
    return trades_info
