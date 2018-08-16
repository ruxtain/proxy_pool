from proxy_pool import db
from proxy_pool.db import Proxy
from proxy_pool import settings
from flask import Flask, request, jsonify
import logging

# hide info output to console
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

@app.route('/')
def index():
    proxy = Proxy.random()
    response = {
        'value': proxy.value,
        'count': proxy.count
    }
    return jsonify(response)

@app.route('/best/')
def best():
    """The new proxy's count is default to 1, so if the count is 0, 
    it means it has been successful for at least once.
    """
    proxy = Proxy.random(max_count=0)
    response = {
        'value': proxy.value,
        'count': proxy.count
    }
    return jsonify(response)

@app.route('/delete/', methods=['GET'])
def delete():
    value = request.args.get('value') # from flask import request
    proxy = Proxy.get({'value': value})
    proxy.delete()
    return 'deleted successfully'

@app.route('/all/')
def get_all():
    proxies = list(Proxy.filter({}))
    total = Proxy.total()
    response = {
        'number': total,
        'proxies': [{'value': proxy.value, 'count': proxy.count} for proxy in proxies],

    }
    return jsonify(response)


def api_run():
    app.run(host=settings.API_HOST, port=settings.API_PORT)

