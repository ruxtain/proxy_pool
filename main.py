from proxy_pool.db import Proxy
from proxy_pool.api import app
from proxy_pool.exam import verify_proxy
from proxy_pool.pool import proxy_getters
from datetime import datetime

import threading
import time
import os
 
def proxy_getter_worker(proxy_getter):
    for proxy_str in proxy_getter.get():
        proxy = Proxy(value=proxy_str, count=0, update=datetime.now())
        while proxy.count <= 3:
            if verify_proxy(proxy_str):
                proxy.count = 0
                proxy.save()
                proxy.status('saved')
                break
            else:
                proxy.count += 1
                if proxy.count > 3:
                    proxy.status('failed')  


def web():
    app.run(port=5001)

def schedule():
    '''
    定时自检
    '''
    retry = 2
    while True:
        time.sleep(300) # 5 min
        for proxy in Proxy.filter(): # all proxy
            if (datetime.now() - proxy.update).total_seconds() > 600: # 10 min
                while proxy.count <= retry:
                    if verify_proxy(proxy.value):
                        proxy.count = 0
                        proxy.update = datetime.now()
                        proxy.save()
                        proxy.status('updated')
                        break
                    else:
                        proxy.count += 1
                if proxy.count > retry:
                    proxy.delete()
                    proxy.status('deleted')

def run():
    webber = threading.Thread(target=web)
    scheduler = threading.Thread(target=schedule)
    webber.start()
    scheduler.start()

    for proxy_getter in proxy_getters:
        t = threading.Thread(target=proxy_getter_worker, args=(proxy_getter,))
        t.start()

if __name__ == '__main__':
    run()



























