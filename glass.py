from keys import api_key, api_secret
from binance.client import Client


class ActiveCoins:
    client = Client(api_key, api_secret)

    def stock_glass(self, coin, level, radius=2, level_coefficient=4):

        """
        Оценка заявки, лежащей рядом с уровнем
        :param coin: Любой фьюч символ (i.e. BTCUSDT)
        :param level: Цена уровня
        :param radius: В каком радиусе от ближайшей цены искать максимальную заявку
        :param level_coefficient: Во сколько раз заявка должна быть больше средней
        :return: True, если заявка хорошая, False, если заявка плохая
        """

        current_price = float(self.client.futures_symbol_ticker(symbol=coin).get('price'))
        glass = self.client.futures_order_book(symbol=coin, limit=1000)
        min_difference = current_price

        # Поиск заявки максимального объёма в радиусе 2 (по дефолту)
        # ордеров от ближайшей цены к указанной

        if level < current_price:
            bids = glass.get('bids')
            closest_bid = self.find_closest_order(level, bids)
            closest_index = closest_bid[0]
            average_order = closest_bid[1]

            # Случай, когда индекс ближайшей цены меньше радиуса

            if radius > closest_index:
                bids = bids[0:closest_index + 2 * radius - closest_index + 1]
            else:
                bids = bids[closest_index - radius: closest_index + radius + 1]

            # Поиск максимальной заявки в указанном радиусе и сравнение со средней заявкой

            max_order = [0, 0]
            for bid in bids:
                if float(bid[1]) > float(max_order[1]):
                    max_order = bid
            if float(max_order[1]) >= level_coefficient * average_order:
                return True
            else:
                return False
        elif level > current_price:
            asks = glass.get('asks')
            closest_ask = self.find_closest_order(level, asks)
            closest_index = closest_ask[0]
            average_order = closest_ask[1]

            # Случай, когда индекс ближайшей цены меньше радиуса

            if radius > closest_index:
                asks = asks[0:closest_index + 2 * radius - closest_index + 1]
            else:
                asks = asks[closest_index - radius: closest_index + radius + 1]

            # Поиск максимальной заявки в указанном радиусе и сравнение со средней заявкой

            max_order = [0, 0]
            for ask in asks:
                if float(ask[1]) > float(max_order[1]):
                    max_order = ask
            if float(max_order[1]) >= level_coefficient * average_order:
                return True
            else:
                return False
        else:
            return False  # Цена совпадает с уровнем

    @staticmethod
    def find_closest_order(level, orders):
        closest_price = float(orders[0][0])
        closest_index = 0
        average_order = 0
        for index, order in enumerate(orders):
            if abs(level - float(order[0])) < abs(level - closest_price):
                closest_price = float(order[0])
                closest_index = index
        for index, order in enumerate(orders[0:closest_index]):
            average_order += float(order[1])
        average_order /= (closest_index + 1)
        return (closest_index, average_order)

# example

# main_class = ActiveCoins()
# print(main_class.stock_glass('BTCUSDT', 20000, radius=6, level_coefficient=6))
