import requests
import time

def verify_proxy(proxy):
    proxies = {"http": "http://{proxy}".format(proxy=proxy)}
    try:
        response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10, verify=False)
        if response.status_code == 200:
            return True
    except:
        return False
