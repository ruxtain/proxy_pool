from proxy_pool import db
from proxy_pool import settings
from flask import Flask, request
import logging

# hide info output to console
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

@app.route('/')
def index():
    return db.Proxy.random().value

@app.route('/delete/', methods=['GET'])
def delete():
    proxy = request.args.get('value') # from flask import request
    try:
        proxy = db.Proxy.objects.get(value=proxy) # django style
        proxy.delete()
        return 'deleted successfully'
    except db.DoesNotExist:
        return "It's already gone!"

@app.route('/all/')
def get_all():
    proxies = db.Proxy.objects.all()
    n = 0
    out = ''
    for proxy in proxies:
        out += '{}<br/>'.format(proxy.value)
        n += 1
    head = '<p>You have <b>{}</b> proxies in total.</p>'.format(n)
    return head + out

def api_run():
    app.run(port=settings.API_PORT)
    
