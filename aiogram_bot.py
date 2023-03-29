from aiogram import Bot, Dispatcher, executor, types
import logging
import asyncio
import requests
import datetime
from keys import Bot_TOKEN
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

storage = MemoryStorage()

logging.basicConfig(level=logging.INFO)

bot = Bot(token=Bot_TOKEN)

dp = Dispatcher(bot, storage=storage)


class States(StatesGroup):
    coin = State()
    price = State()
    current_price = 0


coins = []
lvls = []


async def check_coin(message):
    while True:
        for i in lvls:
            curr_price = get_price(i['coin'])[1]
            lvl_price = i['price']
            if lvl_price * 1.0075 > curr_price > curr_price * 0.0025:
                await bot.send_message(message.from_user.id, f"{i['coin']}, {curr_price}, {lvl_price}")
                lvls.remove(i)

        await asyncio.sleep(1)


# binance funcs
def get_symbols():
    resp = requests.get('https://api.binance.com/api/v1/exchangeInfo')
    for coin in resp.json().get('symbols'):
        if coin.get('symbol').endswith('USDT'):
            coins.append(coin.get('symbol'))


def get_price(coin):
    key = f"https://api.binance.com/api/v3/ticker/price?symbol={coin}"

    data = requests.get(key)
    data = data.json()
    return [datetime.datetime.now().time(), float(data.get('price'))]


@dp.message_handler(commands=['start'])
async def start_bot(message: types.Message) -> None:
    await bot.send_message(message.chat.id, '<b>Привет, трейдер))</b>', parse_mode='html')
    await start_menu(message)


async def start_menu(message: types.Message):
    markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)

    NEW = types.KeyboardButton(text='Новый уровень')
    CHECK = types.KeyboardButton(text='Проверить имеющиеся')

    markup_reply.add(NEW, CHECK)
    await bot.send_message(message.chat.id, '<b>Чего желаешь?</b>', reply_markup=markup_reply, parse_mode='html')


@dp.message_handler(content_types=["text"])
async def answer(message: types.Message):
    if message.text == 'Новый уровень' or message.text == 'Новый уровень':
        get_symbols()
        await bot.send_message(message.chat.id, '<b>Дай монетку</b>', parse_mode='html',
                               reply_markup=types.ReplyKeyboardRemove())
        await States.coin.set()
    if message.text == 'Проверить имеющиеся':
        await bot.send_message(message.from_user.id, f'{lvls}')


@dp.message_handler(state=States.coin, content_types=["text"])
async def get_lvl(message: types.Message, state: FSMContext):
    if message.text.upper() + 'USDT' in coins:
        async with state.proxy() as data:
            data['coin'] = message.text.upper() + 'USDT'
            data['current_price'] = get_price(message.text.upper() + 'USDT')
        await bot.send_message(message.chat.id, '<b>Дай уровень</b>', parse_mode='html')
        await States.next()
    elif message.text.upper() in coins:
        async with state.proxy() as data:
            data['coin'] = message.text.upper()
            data['current_price'] = get_price(message.text.upper())
        await bot.send_message(message.chat.id, '<b>Дай уровень</b>', parse_mode='html')
        await States.next()

    else:
        await bot.send_message(message.chat.id, '<b>Плохая монетка, нада другую</b>', parse_mode='html')


@dp.message_handler(lambda message: message.text.isdigit(), state=States.price, content_types=["text"])
async def set_lvl(message: types.Message, state: FSMContext):
    for i in lvls:
        if i.get('id') == id:
            i['lvl_price'] = message.text
    async with state.proxy() as data:
        data['price'] = float(message.text)
        print(data)
        lvls.append(data)

    await state.finish()
    await start_menu(message)
    await check_coin(message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
