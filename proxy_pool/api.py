from proxy_pool import db
from proxy_pool import settings
from flask import Flask
import logging

# hide info output to console
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

@app.route('/')
def index():
    return db.Proxy.random().value

def api_run():
    app.run(port=settings.API_PORT)
    
