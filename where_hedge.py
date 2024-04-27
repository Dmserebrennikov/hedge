import socket
import pickle
import multiprocessing
from multiprocessing import Process, Manager
import MetaTrader5 as Mt
from broker import Broker


UDP_IP = "127.0.0.1"
# TRANSMISSION_PORT = 8433
RECEIVER_PORT = 8433

PATH = "C:/Program Files/Pepperstone MetaTrader 5/terminal64.exe"
LOGIN = 922208
PASSWORD = "xxx"
SERVER = "DooTechnology-Live"
PREFIX = ""
EXEC_MODE = Mt.ORDER_FILLING_FOK
NAME = "where_hedge"

SYMBOLS_LIST = ["GBPUSD"]

exec_modes = {
    "FOK": Mt.ORDER_FILLING_FOK,
    "IOC": Mt.ORDER_FILLING_IOC,
    "RETURN": Mt.ORDER_FILLING_RETURN,
}


class Side:
    BUY = 0
    SELL = 1


# def transmitter():
#     payload = {
#         "broker": "where_hedge",
#         "action": "entry",
#     }
#     data = pickle.dumps(payload)
#     print("Sending data...")
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # (Internet, UDP)
#     sock.sendto(data, (UDP_IP, TRANSMISSION_PORT))


def process_message(trades_dict, msg):
    print(msg)
    bk = msg.get("broker")
    need_hedge = bk == "need_hedge"
    if not need_hedge:
        print("Unknown message")
    else:
        volume = msg["volume"]
        side = msg["side"]
        opp_side = Side.BUY if side == Side.SELL else Side.SELL
        symbol = msg["symbol"]

        trade_dict = dict()
        trade_dict["side"] = opp_side
        trade_dict["volume"] = volume
        trades_dict[symbol] = trade_dict
        print(f"Hedge position has been added: {symbol}, {volume}, {side}")


def receiver(trades_dict):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # (Internet, UDP)
    sock.bind((UDP_IP, RECEIVER_PORT))
    print("Start receiver loop")
    while True:
        data_bytes, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        print("received message: %s" % data_bytes)
        print("Address:", addr)
        data = pickle.loads(data_bytes)
        process_message(trades_dict, data)


def open_hedge_positions(broker, trades_dict):
    for sym, params in trades_dict.items():
        side = params["side"]
        volume = params["volume"]
        symbol = sym + PREFIX
        res = broker.open_order(symbol, side, volume)
        print(res)
        print(f"Hedge order has been sent: {symbol}, {volume}, {side}")


def run_broker(trades_dict):
    broker = Broker(PATH, LOGIN, PASSWORD, SERVER, SYMBOLS_LIST, PREFIX, EXEC_MODE, NAME)
    print("Start checking for closed trades")
    trades_count = Mt.positions_total()
    while True:
        positions_total = Mt.positions_total()
        if positions_total > trades_count:
            trades_count = positions_total
        elif positions_total < trades_count:
            print("open_hedge_positions call!!!")
            open_hedge_positions(broker, trades_dict)


def run():
    with Manager() as manager:
        positions_to_hedge = manager.dict()

        p1 = Process(target=receiver, args=(positions_to_hedge,))
        p1.start()

        p2 = Process(target=run_broker, args=(positions_to_hedge,))
        p2.start()

        p1.join()
        p2.join()


if __name__ == '__main__':
    run()
