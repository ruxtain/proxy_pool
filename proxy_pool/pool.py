"""
    Multithreads to get proxies from free websites
"""

from proxy_pool import settings
from proxy_pool.db import Proxy
from proxy_pool.utils import print_log
from queue import Queue
import threading
import requests
import random
import time
import re

# turn off unnecessary warnings
requests.packages.urllib3.disable_warnings()

class ProxyWebsite:

    def __init__(self, base_url, pages=range(1,2)):
        self.base_url = base_url
        self.pages = pages
        self.count = -1

    def __iter__(self):
        return self

    def __next__(self):
        self.count += 1
        if self.count < len(self.pages):
            return self.base_url.format(self.pages[self.count])
        else:
            raise StopIteration


def utils_request(url):
    """
    使用代理池的有效代理去爬取更多代理
    如果代理池没有有效代理，则用本机的 IP
    如果失败，不会删除这个有效代理
    因为失败的原因很多，而有效代理很宝贵...
    """
    headers = {'User-Agent': random.choice(settings.USER_AGENTS)}
    try:
        proxy = Proxy.random(max_count=0)
        print_log('Using {} to fetch {}...'.format(proxy.value, url))
        proxies = {'http': proxy.value}
    except IndexError:
        proxies = {}

    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
        if response.status_code == 200:
            return response.text

    except requests.exceptions.ProxyError:
        pass
    except requests.exceptions.ReadTimeout:
        pass
    except requests.exceptions.ConnectionError:
        pass
    except requests.exceptions.ChunkedEncodingError:
        pass

def init_queue(proxy_websites):
    queue = Queue() # unlimited
    url_list = [] 
    for proxy_website in proxy_websites:
        for url in proxy_website:
            url_list.append(url)

    random.shuffle(url_list)
    for url in url_list:
        queue.put(url)
    return queue


def proxy_website_crawler(queue):
    while True:
        # 通过测试的量必须大于池子的SIZE
        # 待测和通过测试的proxy总数小于 POOL_MAX_SIZE
        # 这样做是避免过度爬取代理网站，使本机 IP 被封杀
        if (Proxy.total() < settings.POOL_MAX_SIZE
            and len(list(Proxy.filter({'count': 0}))) < settings.POOL_SIZE): 

            url = queue.get()

            html = utils_request(url)

            if not html:
                continue

            html = re.sub(r'<.*?>', ' ', html)
            html = re.sub(r'\s+', ' ', html)
            values = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*?(\d{2,5})', html)

            for value in values:

                value = '{}:{}'.format(value[0], value[1]) # very important formatting

                p = Proxy(value=value)
                try:
                    Proxy.get({'value': p.value})
                except LookupError:
                    p.save()
                    p.status('add')

            queue.task_done()

        else:
            time.sleep(5)

        
def pool_run():
    # proxy_websites = [
    #     ProxyWebsite('https://seotoolstation.com/free-proxy-list'), # easy
    #     ProxyWebsite('http://www.xicidaili.com/nn/{}', range(1,3000)),
    #     ProxyWebsite('http://www.xicidaili.com/nt/{}', range(1,690)),
    #     ProxyWebsite('http://www.xicidaili.com/wn/{}', range(1,1400)),
    #     ProxyWebsite('http://www.xicidaili.com/wt/{}', range(1,1800)),
    #     ProxyWebsite('http://www.66ip.cn/{}.html', ['index.html'] + list(range(1,1339))), # easy
    #     ProxyWebsite('http://www.ip3366.net/free/?page={}', range(1,7)), # easy
    #     ProxyWebsite('https://www.kuaidaili.com/free/inha/{}/',range(1,1000)), # easy
    #     ProxyWebsite('https://www.kuaidaili.com/free/intr/{}/',range(1,1000)), # easy
    #     ProxyWebsite('http://www.data5u.com/free/{}/index.shtml',['gngn', 'gnpt', 'gwgn', 'gwpt']), # easy
    #     ProxyWebsite('http://www.data5u.com/'), # easy
    #     ProxyWebsite('http://www.89ip.cn/index_{}.html',range(1, 2000)), # easy
    #     ProxyWebsite('http://ip.jiangxianli.com/?page={}',range(1,7)), # easy
    #     ProxyWebsite('http://www.mimiip.com/gngao/{}',range(1,600)), # easy
    # ]    

    proxy_websites = [
        ProxyWebsite('https://seotoolstation.com/free-proxy-list'), # easy
        ProxyWebsite('http://www.xicidaili.com/nn/{}', range(1,100)),
        ProxyWebsite('http://www.xicidaili.com/nt/{}', range(1,100)),
        ProxyWebsite('http://www.xicidaili.com/wn/{}', range(1,100)),
        ProxyWebsite('http://www.xicidaili.com/wt/{}', range(1,100)),
        ProxyWebsite('http://www.66ip.cn/{}.html', ['index.html'] + list(range(1,100))), # easy
        ProxyWebsite('http://www.ip3366.net/free/?page={}', range(1,7)), # easy
        ProxyWebsite('https://www.kuaidaili.com/free/inha/{}/',range(1,100)), # easy
        ProxyWebsite('https://www.kuaidaili.com/free/intr/{}/',range(1,100)), # easy
        ProxyWebsite('http://www.data5u.com/free/{}/index.shtml',['gngn', 'gnpt', 'gwgn', 'gwpt']), # easy
        ProxyWebsite('http://www.data5u.com/'), # easy
        ProxyWebsite('http://www.89ip.cn/index_{}.html',range(1, 100)), # easy
        ProxyWebsite('http://ip.jiangxianli.com/?page={}',range(1,7)), # easy
        ProxyWebsite('http://www.mimiip.com/gngao/{}',range(1,100)), # easy
    ]    

    while True:
        queue = init_queue(proxy_websites)
        print_log('{} URLs are ready to bring you proxies...'.format(queue.qsize()))

        threads = []
        for i in range(settings.POOL_WORKERS):
            thread = threading.Thread(target=proxy_website_crawler, args=(queue,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        queue.join()













