# get proxy from free websites

import requests
import re
import time
import multiprocessing
import sys

sys.path.append('../proxy_pool')

try:
    from proxy_pool import utils
except ModuleNotFoundError:
    import utils

proxy_pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*?(\d{2,5})')
no_tag_pattern = re.compile(r'<.*?>')
no_whitespace_pattern = re.compile(r'\s+')

class ProxyGetter:
    '''
    base_url: omitted
    pages: a list of page index
    processor: do something with the html before applying regex
    clease: a default processor that cleans tags and whitespaces
    '''
    
    PAUSE = 1

    @staticmethod
    def _cleanse(html):
        html = no_tag_pattern.sub('', html)
        html = no_whitespace_pattern.sub(' ', html)
        return html
    def __init__(self, base_url, pages, processor=None, cleanse=False):
        self.base_url = base_url
        self.pages = pages
        self.proxies = self.get()
        self.cleanse = cleanse
        self.processor = processor
    def get(self):
        for page in self.pages:
            url = self.base_url.format(page)
            html = utils.get_html_from_url(url)
            if self.cleanse:
                html = self._cleanse(html)    
            if self.processor:
                html = self.processor(html)
            for proxy in proxy_pattern.findall(html):
                time.sleep(self.PAUSE)
                yield '{}:{}'.format(*proxy)

proxy_getters = [
    ProxyGetter('http://www.xicidaili.com/nn/{}', range(1,30), cleanse=True),
    ProxyGetter('http://www.66ip.cn/{}.html', ['index.html'] + list(range(1,30))),
    ProxyGetter('http://www.ip3366.net/free/?page={}', range(1,7), cleanse=True),
    ProxyGetter('https://www.kuaidaili.com/free/inha/{}/',range(1,10),cleanse=True),
    ProxyGetter('http://www.data5u.com/free/{}/index.shtml',['gngn', 'gnpt', 'gwgn', 'gwpt'],cleanse=True),
    ProxyGetter('http://www.89ip.cn/index_{}.html',range(1, 100),cleanse=True),
]

