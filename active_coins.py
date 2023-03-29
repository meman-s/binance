from binance.client import Client
from api_keys import api_key, api_secret


class main_class():

    client = Client(api_key, api_secret)

    def find_active_coins(self):
        tickers = self.client.futures_ticker()
        active_coins = []
        for ticker in tickers:
            symbol = ticker.get('symbol ')
            if symbol[-1] == 'T':
                priceChangePercent = round(float(ticker.get('priceChangePercent')), 2)
                quoteVolume = round(float(ticker.get('quoteVolume')) / 1000000, 2)
                if abs(priceChangePercent) >= 15 or quoteVolume >= 300:
                    active_coins.append(symbol)
        print(active_coins)
        return active_coins

nsfjdis = main_class()
nsfjdis.find_active_coins()