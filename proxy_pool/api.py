from proxy_pool import db
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return db.Proxy.random().value

if __name__ == '__main__':
    app.run(port=5001)
