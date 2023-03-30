from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from keys import api_key, api_secret


class Trade():

    def __init__(self, level):
        self.lvl = level
        self.client = UMFuturesWebsocketClient()
        self.client.start()

    def stream(self):
        _kline = self.client.kline(symbol='BTCUSDT', id=2, interval='1m', callback=lambda x: print(x))


trade = Trade(123)
trade.stream()