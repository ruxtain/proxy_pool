from proxy_pool.db import Proxy
from proxy_pool.api import api_run
from proxy_pool.exam import exam_run
from proxy_pool.pool import pool_run
from proxy_pool.settings import *
from datetime import datetime

from multiprocessing import Process
import time
import os

def basic_info():
    print('PROXY POOL begins.')
    print('More info can be found here: https://github.com/ruxtain/proxy_pool')
    print('POOL SIZE: {}'.format(POOL_SIZE))
    print('API: http://127.0.0.1:{}'.format(API_PORT))
    print('connecting to: mongodb://{}:{}\n'.format(DB_HOST, DB_PORT))

    print('Always use `CTRL+C` to quit ...(Don\'t use `CTRL+Z`)\n')

def main():
    basic_info()
    p_list = [
        (True, Process(target=pool_run)),
        (False, Process(target=exam_run)),
        (True, Process(target=api_run)),
    ]

    for daemon, p in p_list:
        p.daemon = daemon
        p.start()
    for daemon, p in p_list:
        p.join()

if __name__ == '__main__':
    main()





