'''
策略：
遍历测试代理的有效性，如果失败则 count 加 1
遍历的顺序根据代理的上次更新时间（update_time)，从最古老的开始
当 count 超过某个临界值（DEL_SIGNAL）时删除代理 （临界值暂定为 5）

测试链接 http://httpbin.org/ip （西雅图） 可能需要换成国内网站，
以提高测试的速度。timeout 就可以设置短一点。

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
        response = requests.get('http://httpbin.org/get', headers=headers, proxies=proxies, timeout=8, verify=False)
        if response.status_code == 200:
            return True
    except:
        return False

def exam(proxy):
    '''
    check if a proxy is valid
    delete if it's invalid
    '''
    proxy.status('check')
    if proxy.count < settings.DEL_SIGNAL:
        if verify_proxy(proxy):  # success
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
    '''
    检查的频率主要由 POOL_SIZE 大小和良品率决定。
    '''
    p_num0 = settings.POOL_SIZE//100  # a relation based on experience
    
    while True:
        rate = db.Proxy.quality_rate()
        if rate < 0.1:
            p_num = p_num0 + 15
        elif rate < 0.5:
            p_num = p_num0 + 10
        else:
            p_num = p_num0 + 6

        db.print_log('Using {} processes:'.format(p_num))

        if db.Proxy.total() > 0:
            pool = multiprocessing.Pool(processes=p_num)
            pool.map(exam, db.Proxy.objects.order_by('update_time')) # 从最老的开始
            pool.close()
        else:
            time.sleep(10)












        
