# common functions
# controlled by: suyun/main.py

from proxy_pool import settings

from lxml import etree
import requests
import random
import time

# 关闭所谓不安全链接的提醒
requests.packages.urllib3.disable_warnings()

def get_random_headers():
    return {'User-Agent': random.choice(settings.USER_AGENTS)}

def get_html_from_url(url):
    headers = get_random_headers()
    response = requests.get(url, headers=headers)
    return response.text

    