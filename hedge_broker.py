"""
Script starts MT5 terminal of the broker, where hedging positions will be opened

Usage:
    add_broker.py <path> <login> <password> <server> <prefix> <exec_mode> [<symbols> ...]

Options:
    -h, --help          Show this screen and exit

"""

import MetaTrader5 as Mt
from broker import Broker, EXECUTION
from docopt import docopt
from trade_api import all_positions


def main():
    args = docopt(__doc__)
    path = args["<path>"]
    login = args["<login>"]
    password = args["<password>"]
    server = args["<server>"]
    prefix = args["<prefix>"]
    exec_mode = args["<exec_mode>"]
    exec_mode = EXECUTION[exec_mode]
    symbols = args["<symbols>"]
    print(args)

    broker = Broker(path, login, password, server, symbols, prefix, exec_mode, server)
    print(f"Starting hedge broker")

    trades_count = Mt.positions_total()
    while True:
        positions_total = Mt.positions_total()
        if positions_total > trades_count:
            trades_count = positions_total
        elif positions_total < trades_count:
            print("One of the trade has been closed. Hedge all trades from DB")
            positions = all_positions()
            for symbol, info in positions.items():
                print(symbol)
                print(info)
                side = info["side"]
                volume = info["volume"]
                opp_side = 1 if side == 0 else 0
                broker.open_order(symbol, opp_side, volume)
                print(f"Hedge order has been sent: {symbol}, {volume}, {side}")
            break
    print("All hedge positions have been opened. Stopping the script.")


if __name__ == "__main__":
    main()
