#! /Users/michael/anaconda3/bin/python
# @Date:   2018-09-09 20:53:22

from proxy_pool import db
from proxy_pool import settings
from proxy_pool.db import Proxy
from proxy_pool.utils import print_log

from datetime import datetime
import asyncio
import aiohttp
import concurrent


async def check(proxy):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(settings.EXAM_WEBSITE, proxy="http://{}".format(proxy.value), timeout=10) as response:
                html = await response.text()
                if response.status == 200: # 拿 status 不需要 await
                    return True
    except concurrent.futures._base.TimeoutError:
        return False
    except aiohttp.client_exceptions.ClientProxyConnectionError:
        return False


async def task(proxy, sem):    
    async with sem:
        if 0 < proxy.count < settings.DEL_SIGNAL:
            flag = await check(proxy)
            if flag:  # success
                proxy.count = 0 
                proxy.status('success')
            else:
                proxy.count += 1
                proxy.status('fail')
            proxy.update_time = datetime.now() 
            proxy.save()
        else:
            proxy.status('delete')
            proxy.delete()   


def exam_run():
    while True:
        sem = asyncio.Semaphore(settings.EXAM_CORO)
        tasks = [task(proxy, sem) for proxy in Proxy.aggregate([{"$sort" :{"count": -1, "update_time": 1}}])]
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))



