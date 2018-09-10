# proxy_pool
[![Open Source Love](https://badges.frapsoft.com/os/v2/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/) [![MIT Licence](https://badges.frapsoft.com/os/mit/mit.png?v=103)](https://opensource.org/licenses/mit-license.php)


> Only tested under python3.6 (macOS)

Inspired by the project: [proxy_pool](https://github.com/jhao104/proxy_pool), I want to make a proxy pool with less code and simpler logic.

# How it works

Get proxies from free websites and save them in mongodb.
Check if these proxies are valid periodically with multiprocessing.

# Try it out

There isn't much to do before hand, simply run:
```
python main.py
```

You can get a random proxy with http API, the default port is 5001:
```
import requests
requests.get('http://localhost:5001/get')
```

or remove an invalid proxy like this:
```
import requests
requests.get('http://localhost:5001/delete/?value=123.123.123.123:9000')
```

# Settings

You can see a django style settings.py here. 
The `POOL_SIZE` is the max number of valid proxies.

# Extension

To add more proxy website, you can use just one line like this (proxy_pool/pool.py):
```
# range(1, 30) indicates 1 to 29 pages, of course
ProxyGetter('http://www.xicidaili.com/nn/{}', range(1,30))
```


