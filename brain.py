import socket
import json
import pickle


# Brain:
# - FastAPI service
# - Receives responses and handles this

"""
Это Центр Принятия и Обработки Решений ЦПОР

От акцептора получаем список трейдов на хежд
От донора получаем команду на закрытие позы
Отправляем команду донору на открытие поз

Т.е. есть какая-то база данных. Там хранятся:
- трейды для хеджа
- активные брокеры
"""


# Просто UDP
# Получаем данные от брокеров в режиме лайв
# Обрабатываем, обновляем данные
# Как только у нас открыты позиции в обоих брокерах, начинаем отслеживать закрытие позы


UDP_IP = "127.0.0.1"
UDP_PORT = 8433

TRANSMISSION_PORT = 8434


class Actions:
    ENTRY = "entry"
    EXIT = "exit"


class Side:
    BUY = 0
    SELL = 1


brokers = {
    "to_hedge": {
        "entry": False
    },
    "where_hedge": {
        "entry": False
    }
}


# def send_close_request():
#     print("Sending close request!")
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # (Internet, UDP)
#     sock.sendto(MESSAGE, (UDP_IP, TRANSMISSION_PORT))


def transmitter():
    payload = {
        "broker": "where_hedge",
        "action": "entry",
        "need_hedge": True,
        "volume": 0.01,
        "side": Side.BUY,
        "symbol": "EURUSD"
    }
    data = pickle.dumps(payload)
    print("Sending data...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # (Internet, UDP)
    sock.sendto(data, (UDP_IP, TRANSMISSION_PORT))


def process_message(msg):
    broker = msg["broker"]
    action = msg["action"]
    if action == Actions.ENTRY:
        brokers[broker][action] = True
        print("ENTRY", broker, brokers[broker][action])
    elif action == Actions.EXIT:
        if brokers["to_hedge"]["entry"]:
            pass
            # send_close_request()


def receiver():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # (Internet, UDP)
    sock.bind((UDP_IP, UDP_PORT))
    print("Start receiver loop")

    while True:
        data_bytes, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        print("received message: %s" % data_bytes)
        print("Address:", addr)
        data = pickle.loads(data_bytes)
        process_message(data)


transmitter()
