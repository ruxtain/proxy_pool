# common functions

from proxy_pool import settings

import logging
import random
import time
import os

path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
logfile = os.path.join(path, 'proxy_pool.log')
logging.basicConfig(
    filename=logfile, 
    filemode='a', 
    level=logging.DEBUG,
    datefmt='[%Y-%m-%d %H:%M:%S]',
    format='%(asctime)s %(message)s',
)


def init_log():
    """ clear previous log before running """
    with open(logfile, 'w', encoding='utf-8') as f:
        pass


def print_log(content, level='debug'):
    """ output log to both console and proxy_pool.log file """
    print(content)
    if level == 'debug':
        logging.debug(content)
    elif level == 'info':
        logging.info(content)
    elif level == 'warning':
        logging.warning(content)
    elif level == 'critical':
        logging.critical(content)

    