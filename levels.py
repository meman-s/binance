from binance.spot import Spot
from binance.cm_futures import CMFutures
from binance.client import Client
import time
import datetime
from api_keys import api_key, api_secret

client = Client(api_key='eRcMMpgk2BiwWStefc4Wkm79f1A69xDBIGRdCFQI6jEOi80XsU5VR1NKqlaG3jyu',
                api_secret='YUkEg8eYyIQWVMY3MR9YavaRJaS9qkJw0qxlGzxHzxo1F8B3FVODiHeDJ04JqDhh')


class HighLevel:
    def __init__(self, symbol, interval, limit, dif_time=10, dif_percent=0.0005, vol_percent=0.01, h_l=1,
                 candle_time_secs=3600, laps=1):
        self.symbol = symbol
        self.interval = interval
        self.limit = limit
        self.dif_percent = dif_percent   # percent between two extremums
        self.vol_percent = vol_percent   # precent of etremum candle
        self.extremum = []
        self.can_couples = [[], []]
        self.rez_for_between = [[], []]
        self.rez_for_vol = [[], []]
        self.rez_break = [[], []]
        self.dif_time = dif_time   # amount of candles between two extremums
        self.h_l = h_l  # h_l is for high(1) or low(2) levels
        self.candle_time_secs = candle_time_secs   # time in secs of candle live
        self.laps = laps   # amount of laps for more data
        self.client = Client()
        self.breaks = [[], []]
        self.intouchable = [[], []]

    def get_extremums(self, symbol, interval, limit, laps):
        time_start = client.futures_klines(symbol=symbol, interval=interval, limit=1)
        time_start = time_start[0][0]
        for i in range(0, laps):
            time_start = time_start - 450000000 * i
            sas = client.futures_historical_klines(symbol=self.symbol, interval=interval, limit=limit,
                                                   start_str=time_start - 449700000, end_str=time_start)
            for ind, k in enumerate(sas):
                sas[ind] = [k[0], float(k[2]), float(k[3])]
            self.extremum = sas + self.extremum
        for ind, ex in enumerate(self.extremum):
            self.extremum[ind].append(ind)
        # printing
        # for ex in self.extremum:
        #     print(datetime.datetime.fromtimestamp(ex[0] // 1000), ex[1],
        #           ex[2], ex[3])

    def check_difpercent_distance(self, extremum, dif_percent, dif_time, h_l):
        for index, can_1 in enumerate(extremum):
            count = 0
            for can_2 in extremum[index + 1:]:
                if can_1[h_l] * (1 - dif_percent) < can_2[h_l] < can_1[h_l] * (1 + dif_percent) and abs(
                        can_1[0] - can_2[0]) > dif_time * 1000 * self.candle_time_secs:
                    self.can_couples[h_l - 1].append([can_1, can_2])
                    count += 1
                elif count:
                    break

    def check_betweenmax(self, can_couples, h_l):
        for couple in can_couples[h_l - 1]:
            count = 0
            for candle in self.extremum[couple[0][3] + 1:couple[1][3]]:
                if h_l == 1:
                    if candle[1] >= min(couple[0][1], couple[1][1]):
                        count += 1
                else:
                    if candle[2] <= max(couple[0][2], couple[1][2]):
                        count += 1
            if count == 0:
                self.rez_for_between[h_l - 1].append(couple)

    def check_vol(self, can_couples, vol_percent, h_l):
        for couple in can_couples[h_l - 1]:
            if couple[0][1] / couple[0][2] - 1 > vol_percent and couple[1][1] / couple[1][2] - 1 > vol_percent:
                self.rez_for_vol[h_l - 1].append(couple)

    def print(self):
        self.get_extremums(self.symbol, self.interval, self.limit, self.laps)
        self.check_difpercent_distance(self.extremum, self.dif_percent, self.dif_time, self.h_l)
        self.check_vol(self.can_couples, self.vol_percent, self.h_l)
        self.check_betweenmax(self.rez_for_vol, self.h_l)
        for level in self.rez_for_between[self.h_l - 1]:
            print(datetime.datetime.fromtimestamp(level[0][0] // 1000), level[0][1], level[0][2],
                  '->',
                  datetime.datetime.fromtimestamp(level[1][0] // 1000), level[1][1], level[1][2])

    def level_break(self):
        count = 0
        summa = 0
        for level in self.rez_for_between[self.h_l - 1]:
            lvl_max = max(level[0][1], level[1][1])
            lvl_min = min(level[0][2], level[1][2])
            count_h = 0
            for ex in self.extremum[level[1][3] + 1:]:
                count_m = 0
                if count_h:
                    break
                if self.h_l == 1 and ex[1] > lvl_max:
                    count_h += 1
                    lvl_breaks = client.futures_historical_klines(self.symbol, interval='1m',
                                                                  limit=self.candle_time_secs // 60,
                                                                  start_str=ex[0],
                                                                  end_str=ex[0] + self.candle_time_secs * 1000)
                    for ind, lvl_break in enumerate(lvl_breaks):
                        if count_m:
                            break
                        else:
                            count_m += 1
                            break_percent = (float(lvl_break[2]) - lvl_max) / float(lvl_break[2]) * 100
                            summa += break_percent
                            count += 1
                            self.breaks[self.h_l - 1].append(
                                [level, datetime.datetime.fromtimestamp(lvl_break[0] // 1000),
                                 lvl_break[2], break_percent])
                if self.h_l == 2 and ex[2] < lvl_min:
                    count_h += 1
                    lvl_breaks = client.futures_historical_klines(self.symbol, interval='1m',
                                                                  limit=self.candle_time_secs // 60,
                                                                  start_str=ex[0],
                                                                  end_str=ex[0] + self.candle_time_secs * 1000)
                    for ind, lvl_break in enumerate(lvl_breaks):
                        if count_m:
                            break
                        else:
                            count_m += 1
                            break_percent = abs(float(lvl_break[3]) - lvl_min) / float(lvl_break[3]) * 100
                            self.breaks[self.h_l - 1].append(
                                [level, datetime.datetime.fromtimestamp(lvl_break[0] // 1000),
                                 lvl_break[3], break_percent])
                            summa += break_percent
                            count += 1
            if count_m == 0:
                self.intouchable[self.h_l-1].append(level)
        print(self.breaks)
        print('===========')
        print(self.intouchable)

    # def current_level(self):
    #     for


BTC_level = HighLevel('BTCUSDT', '1h', 1500, dif_time=10, dif_percent=0.001, vol_percent=0.004, h_l=2,
                      candle_time_secs=3600, laps=1)
BTC_level.print()
print('===========')
BTC_level.level_break()
