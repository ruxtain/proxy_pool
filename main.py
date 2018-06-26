from proxy_pool.api import api_run
from proxy_pool.exam import exam_run
from proxy_pool.pool import pool_run
from proxy_pool.settings import *
from proxy_pool.db import print_log, init_log

from multiprocessing import Process
from datetime import datetime

def basic_info():
    print_log('PROXY POOL begins.')
    print_log('More info can be found here: https://github.com/ruxtain/proxy_pool')
    print_log('POOL SIZE: {}'.format(POOL_SIZE))
    print_log('API: http://127.0.0.1:{}'.format(API_PORT))
    print_log('connecting to: mongodb://{}:{}\n'.format(DB_HOST, DB_PORT))

    print_log('Always use `CTRL+C` to quit ...(Don\'t use `CTRL+Z`)\n')

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
    init_log()
    main()





