# get proxy from free websites

from proxy_pool import settings
from proxy_pool import utils
from proxy_pool import db

from urllib.parse import urlparse
from datetime import datetime
import multiprocessing
import mongoengine
import requests
import random
import time
import sys
import re

proxy_pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*?(\d{2,5})')
no_tag_pattern = re.compile(r'<.*?>')
no_whitespace_pattern = re.compile(r'\s+')

class ProxyGetter:
    """base_url: the basic url of the proxy website
    pages: a list of page index
    processor: do something with the html before applying regex
    clease: a default processor that cleans tags and whitespaces
    """

    def __init__(self, base_url, pages, processor=None, cleanse=False):
        self.base_url = base_url
        self.pages = pages
        self.cleanse = cleanse
        self.processor = processor

    @staticmethod
    def _cleanse(html):
        html = no_tag_pattern.sub('', html)
        html = no_whitespace_pattern.sub(' ', html)
        return html   

    def get(self):
        for page in self.pages:
            url = self.base_url.format(page)
            html = utils.get_html_from_url(url)
            if self.cleanse:
                html = self._cleanse(html)    
            if self.processor:
                html = self.processor(html)
            for proxy in proxy_pattern.findall(html):
                yield '{}:{}'.format(*proxy)


def processor_coderbusy(html):
    """ An example of `processor` """

    return re.sub(r' \d{2}\.\d{2} ', ' ', html)


def pool_run():
    """You can easily extend the free proxy website list with just one line,
    if the ProxyGetter._cleanse method is not enough to parse the page,
    you can use the `processor` parameter to write your own `_cleanse`.
    An example of custom `processor` is listed above: `processor_coderbusy`.
    """

    proxy_getters = [
        ProxyGetter('http://www.xicidaili.com/nn/{}', range(1,30), cleanse=True),
        ProxyGetter('http://www.66ip.cn/{}.html', ['index.html'] + list(range(1,30))),
        ProxyGetter('http://www.ip3366.net/free/?page={}', range(1,7), cleanse=True),
        ProxyGetter('https://www.kuaidaili.com/free/inha/{}/',range(1,10),cleanse=True),
        ProxyGetter('http://www.data5u.com/free/{}/index.shtml',['gngn', 'gnpt', 'gwgn', 'gwpt'],cleanse=True),
        ProxyGetter('http://www.89ip.cn/index_{}.html',range(1, 100),cleanse=True),
        ProxyGetter('http://ip.jiangxianli.com/?page={}',range(1,4), cleanse=True),
        ProxyGetter('http://www.mimiip.com/gngao/{}',range(1,100), cleanse=True),
        ProxyGetter('https://proxy.coderbusy.com/classical/https-ready.aspx?page={}',range(1,100), processor=processor_coderbusy, cleanse=True),
    ]

    random.shuffle(proxy_getters) # avoid hit the same website repeatively

    while True:
        for proxy_getter in proxy_getters:
            parsed_url = urlparse(proxy_getter.base_url)
            url = '{}://{}'.format(parsed_url.scheme, parsed_url.netloc)
            db.print_log('Grabbing proxies from: {}'.format(url))
            for proxy in proxy_getter.get():
                if db.Proxy.total() < settings.POOL_SIZE: 
                    p = db.Proxy(value=proxy)
                    try:
                        result = p.save()
                    except mongoengine.errors.NotUniqueError:
                        continue
                    if result:
                        p.status('add')
                    else:
                        p.status('get')
                else:
                    time.sleep(10)


#############
#  Testing  #
#############

def test_processor(html):
    return re.sub(r' \d{2}\.\d{2} ', ' ', html)

def main():
    import time
    base_url = 'https://proxy.coderbusy.com/classical/https-ready.aspx?page={}'
    for proxy in ProxyGetter(base_url,range(1,100), processor=test_processor, cleanse=True).get():
        time.sleep(0.3)

