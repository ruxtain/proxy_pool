from proxy_pool.api import api_run
from proxy_pool.exam import exam_run
from proxy_pool.pool import pool_run
from proxy_pool.settings import POOL_SIZE, API_PORT, DB_HOST, DB_PORT
from proxy_pool.utils import print_log, init_log

import threading
import multiprocessing
from datetime import datetime

import pymongo

def basic_info():
    print_log('Your PROXY POOL begins.')
    print_log('More info can be found here: https://github.com/ruxtain/proxy_pool')
    print_log('You can check out log here: proxy_pool/proxy_pool.log')
    print_log('POOL SIZE: {}'.format(POOL_SIZE))
    print_log('API: http://127.0.0.1:{}'.format(API_PORT))
    print_log('Database: mongodb://{}:{}\n'.format(DB_HOST, DB_PORT))
    print_log('Always use `CTRL+C` to quit ...(Don\'t use `CTRL+Z`)\n')


def main():
    """
    因为 exam 是异步进行访问，因此如果这里使用线程的话，会出现类似：
    RuntimeError: There is no current event loop in thread 'Thread-2'.
    的问题。使用进程可以防止相互之间的干扰。
    """
    basic_info()

    pool = multiprocessing.Process(target=pool_run)
    exam = multiprocessing.Process(target=exam_run)
    api = multiprocessing.Process(target=api_run)

    pool.start()
    exam.start()
    api.start()


if __name__ == '__main__':
    init_log()  # 新建空的日志，如果不存在的话
    main()        



