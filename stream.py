from binance.client import Client
from bd import DB


client = Client(api_key='eRcMMpgk2BiwWStefc4Wkm79f1A69xDBIGRdCFQI6jEOi80XsU5VR1NKqlaG3jyu',
                api_secret='YUkEg8eYyIQWVMY3MR9YavaRJaS9qkJw0qxlGzxHzxo1F8B3FVODiHeDJ04JqDhh')
db = DB('data_base.db')

time = 0
while True:
    data = client.futures_symbol_ticker(symbol='BTCUSDT')
    db.put_data(data.get('symbol'), data.get('price'), data.get('time'))
