from proxy_pool import db
from proxy_pool.db import Proxy
from proxy_pool import settings
from flask import Flask, request
import logging

# hide info output to console
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

@app.route('/')
def index():
    return Proxy.random().value

@app.route('/best/')
def best():
    """The new proxy's count is default to 1, so if the count is 0, 
    it means it has been successful for at least once.
    """
    return Proxy.random(0).value

@app.route('/delete/', methods=['GET'])
def delete():
    value = request.args.get('value') # from flask import request
    proxy = Proxy.get({'value': value})
    proxy.delete()
    return 'deleted successfully'

@app.route('/all/')
def get_all():
    proxies = Proxy.filter({})
    n = 0
    out = ''
    for proxy in proxies:
        out += '{}<br/>'.format(proxy.value)
        n += 1
    head = '<p>You have <b>{}</b> proxies in total.</p>'.format(n)
    return head + out

def api_run():
    app.run(port=settings.API_PORT)
    
