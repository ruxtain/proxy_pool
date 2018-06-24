proxy_pool
======

> Only tested under python3.6 (macOS)

Inspired by the project: [proxy_pool](https://github.com/jhao104/proxy_pool), I want to make a proxy pool with less code and simpler logic.

# How it works

Get proxies from free websites and save them in mongodb.
Check if these proxies are valid periodically with multiprocessing.

# Try it out

There isn't much to do before hand, simple run:
```
pip install -r requriements.txt
python main.py
```

You can get a random proxy with http API, the default port is 5001:
```
import requests
requests.get('http://localhost:5001')
```

or remove an invalid proxy like this:
```
import requests
requests.get('http://localhost:5001/delete/?value=123.123.123.123:9000')
```

# settings

You can see a django style settings.py here. 
The `POOL_SIZE` is the max number of proxies you put in the pool.
You can configure it according to your needs.

# Extension

To add more proxy website, you can use just one line like this (proxy_pool/pool.py):
```
ProxyGetter('http://www.xicidaili.com/nn/{}', range(1,30), cleanse=True)
```
