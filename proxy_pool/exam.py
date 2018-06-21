'''
Check if a proxy is valid.
'''

from proxy_pool import utils
from proxy_pool import db
from proxy_pool import settings

from datetime import datetime
import multiprocessing
import requests
import time

def verify_proxy(proxy):
    proxies = {"http": "http://{proxy}".format(proxy=proxy.value)}
    headers = utils.get_random_headers()
    try:
        response = requests.get('http://httpbin.org/ip', headers=headers, proxies=proxies, timeout=8, verify=False)
        if response.status_code == 200:
            return True
    except:
        return False

def exam(proxy):
    proxy.status('check')
    retry = 2
    while proxy.count <= retry:
        if verify_proxy(proxy):
            proxy.count = 0
            proxy.update = datetime.now()
            proxy.status('update')
            proxy.save()
            break
        else:
            proxy.count += 1
    if proxy.count > retry:
        proxy.status('delete')
        proxy.delete()

def exam_run():
    '''
    No need to check the proxy too frequently if POOL_SIZE is small.
    '''
    p_num = settings.POOL_SIZE//100 + 6 # a relation based on experience
    while True:
        if db.Proxy._count() > 0:
            pool = multiprocessing.Pool(processes=p_num)
            pool.map(exam, db.Proxy.filter())
            pool.close()
        else:
            time.sleep(10)













        
