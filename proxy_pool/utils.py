# common functions
# controlled by: suyun/main.py

from proxy_pool import settings

from lxml import etree
import requests
import logging
import random
import time
import os


# 关闭所谓不安全链接的提醒
requests.packages.urllib3.disable_warnings()

def get_random_headers():
    return {'User-Agent': random.choice(settings.USER_AGENTS)}

def get_html_from_url(url):
    headers = get_random_headers()
    response = requests.get(url, headers=headers)
    return response.text


path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
logfile = os.path.join(path, 'proxy_pool.log')
logging.basicConfig(
    filename=logfile, 
    filemode='a', 
    level=logging.DEBUG,
    datefmt='[%Y-%m-%d %H:%M:%S]',
    format='%(asctime)s %(message)s',
)
# 因为 proxy 的状态需要打印到日志，所以把日志配置到这里，以及把 print_log 定义到这里
# 之所以用 a 模式是因为多进程写日志用 w 只能允许某一个进程写入，
# 用 a 的话，每次允许程序前清空日志，可以达到类似 w 的效果。

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

    