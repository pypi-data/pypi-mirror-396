#
# Set shebang if needed
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 17:21:46 2025

@author: mano
"""


#import test1
#import test2
import asyncio
import time

#A1 = test1.A1
#A2 = test2.A2

#print(A1 is A2)


class Test():
    def __init__(self):
        self.last_time = None
        return None

    def get(self):
        self.last_time = time.time()
        print('Get called', self.last_time)
        return None

    async def loop(self):
        print('Loop started.')
        while True:
            if self.last_time is None:
                print('Loop ended.', time.time(), self.last_time)
                return None
            elif (time.time() - self.last_time) >= 60:
                print('Loop ended.', time.time(), self.last_time)
                return None
            else:
                await asyncio.sleep(60)
                print('Loop restarted.', time.time(), self.last_time)
        return None

    def retrieve(self):
        asyncio.create_task(self.loop(), name='Loop')
        return None

for t in asyncio.all_tasks():
    print(t)

T = Test()
async def f():
    print('f executed')
    await asyncio.sleep(5)
    T.get()
    await asyncio.sleep(5)
    T.retrieve()
    await asyncio.sleep(5)
    T.get()
    await asyncio.sleep(5)
    T.get()
    await asyncio.sleep(5)
    T.get()

    return None

asyncio.create_task(f())




