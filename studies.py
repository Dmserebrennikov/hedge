import multiprocessing
import time


# RECEIVER CODE BELOW

import socket


def receiver():
    # UDP_IP = "35.236.182.158"
    UDP_IP = "127.0.0.1"
    UDP_PORT = 8433

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # (Internet, UDP)
    sock.bind((UDP_IP, UDP_PORT))
    print("Start receiver loop")

    while True:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        print("received message: %s" % data)
        print("Address:", addr)



# TRANSMITTER CODE BELOW

# import socket


def transmitter():
    # UDP_IP = "185.127.18.182"
    IP = "127.0.0.1"
    PORT = 8433
    MESSAGE = b"Hello, World!"

    print("UDP target IP: %s" % IP)
    print("UDP target port: %s" % PORT)
    print("message: %s" % MESSAGE)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # (Internet, UDP)

    sock.sendto(MESSAGE, (IP, PORT))


def run():
    p1 = multiprocessing.Process(target=receiver)
    p1.start()
    time.sleep(3)
    transmitter()


if __name__ == '__main__':
    run()

