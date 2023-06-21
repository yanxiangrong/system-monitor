from datetime import timedelta
from statistics import mean
from typing import Callable

from flask import Flask, render_template
from flask_sock import Sock, Server, ConnectionClosed

from data_collection import system_status
from data_collection.utils import round_half_up
from flaskr.db import get_database
from monitor import Monitor
from utils import *

app = Flask(__name__)
sock = Sock(app)
db = get_database()
monitor = Monitor(db['status'])


def sample(data: Iterable, span: int, sample_func: Callable):
    result = []
    t_data = []
    t_time = 0
    for i in data:
        if t_time == 0:
            t_time = int(i['time'].timestamp()) // span
        if int(i['time'].timestamp()) // span == t_time:
            t_data.append(i)
        elif len(t_data) != 0:
            val = sample_func(t_data)
            val['time'] = datetime.fromtimestamp((t_time + 0.5) * span)
            result.append(val)

            t_time = int(i['time'].timestamp()) // span
            t_data.clear()
            t_data.append(i)
    return result


def sample_func(data: Iterable):
    ret = {}
    func = [cpu_sample, memory_sample, swap_sample, disk_parts_sample, disk_io_sample, net_io_sample]
    for f in func:
        try:
            ret |= f(data)
        except KeyError:
            pass
    return ret


def cpu_sample(data: Iterable):
    core_percents = {}
    for i in data:
        for cpu in i['cpu']:
            if cpu['core'] not in core_percents:
                core_percents[cpu['core']] = []
            core_percents[cpu['core']].append(cpu['percent'])
    return {
        'cpu': [{
            'core': i,
            'percent': round_half_up(mean(core_percents[i]), '0.1')
        } for i in core_percents]
    }


def memory_sample(data: Iterable, key: str = 'memory'):
    percent = []
    total = []
    used = []
    for i in data:
        percent.append(i[key]['percent'])
        total.append(i[key]['total'])
        used.append(i[key]['used'])
    return {
        key: {
            'total': round_half_up(max(total)),
            'used': round_half_up(mean(used)),
            'percent': round_half_up(mean(percent), '0.1')
        }
    }


def swap_sample(data: Iterable):
    return memory_sample(data, 'swap')


def disk_parts_sample(data: Iterable):
    device_data = {}
    for i in data:
        for device in i['disk_parts']:
            dev_name = device['device']
            mountpoint = device['mountpoint']
            if dev_name not in device_data:
                device_data[dev_name] = {
                    'device': dev_name,
                    'mountpoint': mountpoint,
                    'total': [],
                    'used': [],
                    'percent': []
                }
            device_data[dev_name]['total'].append(device['total'])
            device_data[dev_name]['used'].append(device['used'])
            device_data[dev_name]['percent'].append(device['percent'])
    return {
        'disk_parts': [{
            'device': device_data[i]['device'],
            'mountpoint': device_data[i]['mountpoint'],
            'total': round_half_up(max(device_data[i]['total'])),
            'used': round_half_up(mean(device_data[i]['used'])),
            'percent': round_half_up(mean(device_data[i]['percent']), '0.01')
        } for i in device_data]
    }


def disk_io_sample(data: Iterable, key: str = 'disk_io', read_key: str = 'read', write_key='write'):
    device_data = {}
    for i in data:
        for device in i[key]:
            dev_name = device['device']
            if dev_name not in device_data:
                device_data[dev_name] = {
                    'device': dev_name,
                    read_key: [],
                    write_key: []
                }
            device_data[dev_name][read_key].append(device[read_key])
            device_data[dev_name][write_key].append(device[write_key])
    return {
        key: [{
            'device': device_data[i]['device'],
            read_key: round_half_up(mean(device_data[i][read_key])),
            write_key: round_half_up(mean(device_data[i][write_key]))
        } for i in device_data]
    }


def net_io_sample(data: Iterable):
    return disk_io_sample(data, 'net_io', 'send', 'recv')


@app.route("/")
def index():
    return render_template("index.html")


@sock.route('/data')
def echo(ws: Server):
    historical = db['status'].find({'time': {'$gte': datetime.now() - timedelta(days=1)}})
    historical = list(historical)
    for item in historical:
        del item['_id']

    span = int(timedelta(minutes=5).total_seconds())

    values = sample(historical, span, sample_func)
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

        values = sample(new_record, span, sample_func)
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

    app.run(debug=True)


if __name__ == '__main__':
    main()
