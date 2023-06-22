from datetime import timedelta

from flask import Flask, render_template
from flask_sock import Sock, Server, ConnectionClosed

from src import system_status
from src.db.db import get_database
from src.monitor.monitor import Monitor
from src.sample.sample import all_sample, sample
from src.utils import *

route_prefix = '/ctyxdn'

app = Flask(__name__, static_url_path=f'{route_prefix}/static')
sock = Sock(app)
db = get_database()
monitor = Monitor(db['systemMonitor'])


@app.route(f"{route_prefix}/")
def index():
    return render_template("index.html")


@sock.route(f'{route_prefix}/data')
def echo(ws: Server):
    historical = db['systemMonitor'].find({'time': {'$gte': datetime.now() - timedelta(days=1)}})
    historical = list(historical)
    for item in historical:
        del item['_id']

    span = int(timedelta(minutes=5).total_seconds())

    values = sample(historical, span, all_sample)
    data = to_json(values)
    ws.send(data)

    old_values = values[-1]
    values.clear()
    historical.clear()
    while True:
        update_time: datetime = monitor.wait_update()
        if int(update_time.timestamp()) // span <= int(old_values['time'].timestamp()) // span:
            continue

        new_record = db['status'].find({'time': {'$gte': old_values['time']}})
        new_record = list(new_record)
        if len(new_record) == 0:
            continue
        for item in new_record:
            del item['_id']

        values = sample(new_record, span, all_sample)
        new_record.clear()

        if len(values) == 0:
            continue

        if values[0]['time'] == old_values['time']:
            values.pop(0)

        if len(values) == 0:
            continue

        old_values = values[-1]

        data = to_json(values)
        values.clear()
        try:
            ws.send(data)
        except ConnectionClosed:
            break


def init():
    system_status.init()


def main():
    init()
    monitor.start()
    app.run(port=8081)


if __name__ == '__main__':
    main()
