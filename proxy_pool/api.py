from proxy_pool import db
from proxy_pool.db import Proxy
from proxy_pool import settings
from flask import Flask, request, jsonify
import logging

# hide info output to console
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

help_text = {
    "/": "display help information",
    "/get": "get a valid proxy",
    "/delete": "delete a give proxy like this: /delete?value=123.123.123.123:8888",
    "/all": "display all proxies",
    "/status": "basic information of the proxy pool"
}

@app.route('/')
def index():
    return jsonify(help_text)

@app.route('/get/')
def get():
    """The new proxy's count is default to 1, so if the count is 0, 
    it means it has been successful for at least once.
    """
    try:
        proxy = Proxy.random(max_count=0)
        response = {
            'value': proxy.value,
            'count': proxy.count
        }
        return jsonify(response)
    except IndexError:
        return jsonify({"count": "", "value": ""})

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

@app.route('/status/')
def status():
    total = Proxy.total()
    count_0 = Proxy.get_collection().find({'count': 0}).count()
    count_1 = Proxy.get_collection().find({'count': 1}).count()
    count_2 = Proxy.get_collection().find({'count': 2}).count()
    response = {
        'total': total,
        'count_0': count_0,
        'count_1': count_1,
        'count_2': count_2,
    }
    return jsonify(response)


def api_run():
    app.run(host=settings.API_HOST, port=settings.API_PORT)

