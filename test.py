import random
import asyncio
import time

lvl = []

async def check_coin():
    while True:
        for i in lvl:
            curr_price = int(i[0])
            lvl_price = int(i[1])
            if abs(lvl_price - curr_price) < lvl_price * 0.9:
                print('ALARM')
                print(lvl)
        await asyncio.sleep(5)

def tg():
    for i in range(2):
        a, b  = input().split()
        lvl.append([a, b])
        asyncio.run(check_coin())

def pr():
    while True:
        time.sleep(1)
        print(1)

# async def main():
#     task1 = asyncio.create_task(check_coin())
#     task2 = asyncio.create_task(tg())
#     task3 = asyncio.create_task(pr())
#
#     await task1
#     await task2
#     await task3
#
# asyncio.run(main())

tg()
pr()
