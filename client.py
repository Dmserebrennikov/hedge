"""
Script starts MT5 terminal of the broker, which requires hedging of positions

Usage:
    client.py <path> <login> <password> <server> <prefix> <exec_mode> [<symbols> ...]

Options:
    -h, --help          Show this screen and exit

"""

import MetaTrader5 as Mt

from broker import Broker, EXECUTION
from docopt import docopt
from trade_api import new_position
from logger import logger


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
    logger.info(f"Starting broker: {args}")
    Broker(path, login, password, server, symbols, prefix, exec_mode, server)

    logger.info(f"Start tracking new trades in {server}")
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
                new_position(symbol, volume, side)
                logger.info(f"New trade {symbol}, volume: {volume}, side: {side}. Sending info to the decision center")
            trades_count = positions_total


if __name__ == "__main__":
    main()
