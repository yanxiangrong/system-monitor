import time
from datetime import timedelta

from flask import Flask, render_template
from flask_sock import Sock, Server, ConnectionClosed

from data_collection import system_status
from flaskr.db import get_database
from monitor import Monitor
from utils import *

app = Flask(__name__)
sock = Sock(app)
db = get_database()


@app.route("/")
def index():
    return render_template("index.html")


@sock.route('/data')
def echo(ws: Server):
    now = datetime.now()
    historical = db['status'].find({'time': {'$gte': now - timedelta(days=1)}})
    historical = list(historical)
    for item in historical:
        del item['_id']
    data = to_json(historical)
    ws.send(data)
    while True:
        time.sleep(2)
        new_record = db['status'].find({'time': {'$gte': now}})
        now = datetime.now()
        new_record = list(new_record)
        if len(new_record) == 0:
            continue
        for item in new_record:
            del item['_id']
        data = to_json(new_record)
        try:
            ws.send(data)
        except ConnectionClosed:
            break


def init():
    system_status.init()


def main():
    init()
    Monitor(db['status']).start()

    app.run(debug=True)


if __name__ == '__main__':
    main()
