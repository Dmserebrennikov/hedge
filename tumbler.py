"""
Script starts MT5 terminal of the broker, which requires hedging of positions

Usage:
    tunmbler.py <path> <login> <password> <server> <prefix> <exec_mode> [<symbols> ...]

Options:
    -h, --help          Show this screen and exit

"""

import MetaTrader5 as Mt

from broker import Broker, EXECUTION
from docopt import docopt
from logger import logger
import psutil
from time import sleep


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
            sleep(1)
            for process in psutil.process_iter(['pid', 'name', 'cmdline']):
                if process.name() == "terminal.exe":
                    logger.info(f"Killing the process {process}")
                    process.kill()
                if process.name() == "javaw.exe":
                    logger.info(f"Killing the process {process}")
                    process.kill()
            break


if __name__ == "__main__":
    main()
