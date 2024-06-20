import MetaTrader5 as Mt
from time import sleep


MT_RESPONSE_DONE = 10009
MT_RESPONSE_NO_CHANGES = 10025
MT_RESPONSE_MARKET_CLOSE = 10018
MT_RESPONSE_INVALID_STOP = 10016


EXECUTION = {
    "FOK": Mt.ORDER_FILLING_FOK,
    "IOC": Mt.ORDER_FILLING_IOC,
    "RETURN": Mt.ORDER_FILLING_RETURN,
}


class Broker:
    def __init__(self, path, login, password, server, symbols_list, prefix, exec_mode, name):
        print("Starting new broker class. Name", name)
        self.path = path
        self.login = login
        self.password = password
        self.server = server
        self.symbols_list = symbols_list
        self.prefix = prefix
        self.full_symbol_list = [sym + prefix for sym in symbols_list]
        print("self.full_symbol_list", self.full_symbol_list)
        self.exec_mode = exec_mode
        self.name = name
        self.initialize_mt5()
        self.select_symbols()

    def initialize_mt5(self):
        Mt.initialize(self.path, login=self.login, password=self.password, server=self.server)
        sleep(5)
        if not Mt.initialize():
            print(f"initialize() failed, error code = {Mt.last_error()}")
            raise AttributeError("Can't start MT5")

    def select_symbols(self):
        for symbol in self.full_symbol_list:
            selected = Mt.symbol_select(symbol, True)
            sleep(5)
            if not selected:
                raise AttributeError(f"Failed to select {symbol}")
            else:
                print(f"{symbol} has been selected")

    @staticmethod
    def get_price(ask_or_bid, symbol):
        tick_data = Mt.symbol_info_tick(symbol)
        return tick_data.ask if ask_or_bid == "ask" else tick_data.bid

    def open_order(self, symbol, side, volume):
        """
        Function responsible for opening a trade

        param symbol: symbol to trade
        param side: side to trade (Side.SELL / Side.BUY)
        param volume: volume to trade
        param sl: stop loss price
        param pending: defines if the trade is pending or not (there is a special logic for pending trades)
        param tag: trade's tag (originally is used for cascading entry feature as a cascade identifier)

        returns True (open success) / False
        """
        symbol_full = symbol + self.prefix
        request = {
            "action": Mt.TRADE_ACTION_DEAL,
            "symbol": symbol_full,
            "volume": volume,
            "type": side,
            "deviation": 20,
            "comment": "python script",
            "type_time": Mt.ORDER_TIME_GTC,
            "type_filling": self.exec_mode,
        }

        res = Mt.order_send(request)

        if res is None:
            print(f" - {symbol} - Open order failed: no response from MT5")
            return False

        # elif res.retcode == MT_RESPONSE_DONE:
        #     ticket = res.order
        #     open_price = None
        #     curr_trade = None
        #     # Give some time to broker to execute the trade
        #     for _ in range(MAX_ATTEMPTS_MT_INTERACTION):
        #         curr_trade = self.get_last_open_trade()
        #         if curr_trade is None:
        #             time.sleep(DEFAULT_SLEEP)
        #         elif curr_trade.ticket != ticket:
        #             time.sleep(DEFAULT_SLEEP)
        #         else:
        #             open_price = curr_trade.price_open
        #             break
        #     if not open_price:
        #         self.logger.critical(f" - {symbol} - ORDER HAS BEEN SENT BUT NOT EXECUTED ON THE BROKER'S SIDE")
        #         raise
        #     executed_at = datetime.now(tz=NY_TZ)
        #     self._handle_order_open_success(curr_trade, sl, pending, tag, entry_calc, entry_placed_at, executed_at)
        #     return True
        #
        # elif res.retcode == MT_RESPONSE_MARKET_CLOSE:  # Market closed
        #     # Although the market is closed, the order can be executed once the market opens.
        #     # Consequently we should take a relatively long delay to prevent opening of two similar orders
        #     self.logger.warning("MARKET IS CLOSED. TIME SLEEP FOR 1.5 MINUTE")
        #     time.sleep(90)
        #     return False
        # else:
        #     self.logger.warning(f" - {symbol} - OPEN ORDER FAILED: {res.comment}")
        #     return False