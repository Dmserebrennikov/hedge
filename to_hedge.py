import socket
import pickle
import multiprocessing
import MetaTrader5 as Mt
from broker import Broker
from time import sleep


UDP_IP = "127.0.0.1"
TRANSMISSION_PORT = 8433
RECEIVER_PORT = 8434

exec_modes = {
    "FOK": Mt.ORDER_FILLING_FOK,
    "IOC": Mt.ORDER_FILLING_IOC,
    "RETURN": Mt.ORDER_FILLING_RETURN,
}


PATH = "C:/Program Files/MEX MetaTrader 5/terminal64.exe"
LOGIN = 563295
PASSWORD = "xxx"
SERVER = "MEXAtlantic-Real"
PREFIX = ".ecn"
EXEC_MODE = Mt.ORDER_FILLING_FOK
NAME = "to_hedge"

SYMBOLS_LIST = ["GBPUSD"]

# broker = Broker(path, login, password, server, symbols_list, prefix, exec_mode, name)


def transmitter():
    payload = {
        "broker": "where_hedge",
        "action": "entry",
    }
    data = pickle.dumps(payload)
    print("Sending data...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # (Internet, UDP)
    sock.sendto(data, (UDP_IP, TRANSMISSION_PORT))


def process_message(msg):
    need_hedge = msg["need_hedge"]
    if need_hedge:
        volume = msg["volume"]
        side = msg["side"]
        symbol = msg["symbol"]
        broker.open_order(symbol, side, volume)
        # open trade
        print("Hi, we need HEDGE!!!")


def receiver():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # (Internet, UDP)
    sock.bind((UDP_IP, RECEIVER_PORT))
    print("Start receiver loop")

    while True:
        data_bytes, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        print("received message: %s" % data_bytes)
        print("Address:", addr)
        data = pickle.loads(data_bytes)
        process_message(data)


# def initialize_mt5(path, login, password, server):
#     Mt.initialize(path, login=login, password=password, server=server)
#     if not Mt.initialize():0
#         print(f"initialize() failed, error code = {Mt.last_error()}")
#         quit()


def send_hedge_request(order_volume, order_side, order_symbol):
    payload = {
        "broker": "need_hedge",
        "action": "entry",
        "volume": order_volume,
        "side": order_side,
        "symbol": order_symbol
    }
    data = pickle.dumps(payload)
    print(f"Sending hedge request: {order_symbol}, {order_volume}, {order_side}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data, (UDP_IP, TRANSMISSION_PORT))


def run_broker():
    broker = Broker(PATH, LOGIN, PASSWORD, SERVER, SYMBOLS_LIST, PREFIX, EXEC_MODE, NAME)
    print("Starting check for new trades")
    trades_count = Mt.positions_total()
    while True:
        positions = Mt.positions_get()
        if positions is None:
            continue
        positions_total = len(positions)
        if positions_total > trades_count:
            new_trades_count = positions_total - trades_count
            new_trades = positions[-new_trades_count:]
            for trade in new_trades:
                volume = trade.volume
                side = trade.type
                symbol = trade.symbol[:6]
                send_hedge_request(volume, side, symbol)
            trades_count = positions_total


def run():
    p1 = multiprocessing.Process(target=receiver)
    p1.start()

    p2 = multiprocessing.Process(target=run_broker)
    p2.start()

    p1.join()
    p2.join()


if __name__ == '__main__':
    run()

# transmitter()
# send_hedge_request(0.02, 1, "USDCAD")
