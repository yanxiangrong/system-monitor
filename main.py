import re
import time
from datetime import datetime
from decimal import Decimal
from typing import Iterable

import clickhouse_connect
import psutil

from utils import *


def get_time():
    now_time = datetime.now()
    # print(f'time={now_time}')
    return now_time


def get_status():
    s_cpu = psutil.cpu_percent(interval=None, percpu=True)
    if not isinstance(s_cpu, Iterable):
        s_cpu = [s_cpu]
    cpu = [{
        'core': i,
        'percent': s_cpu[i]
    } for i in range(psutil.cpu_count())]
    # print(f'{cpu=}')

    s_vmem = psutil.virtual_memory()
    memory = {
        'total': round_half_up(s_vmem.total / 1024 ** 3),
        'used': round_half_up((s_vmem.total - s_vmem.available) / 1024 ** 3),
        'percent': s_vmem.percent
    }
    # print(f'{memory=}')

    s_swap = psutil.swap_memory()
    swap = {
        'total': round_half_up(s_swap.total / 1024 ** 3),
        'used': round_half_up(s_swap.used / 1024 ** 3),
        'percent': s_swap.percent
    }
    # print(f'{swap=}')

    s_disk_part = psutil.disk_partitions()
    disk_parts = [{
        'device': p.device,
        'mountpoint': p.mountpoint,
    } for p in s_disk_part]
    for p in disk_parts:
        usage = psutil.disk_usage(p['mountpoint'])
        p |= {
            'total': round_half_up(usage.total / 1024 ** 3),
            'used': round_half_up(usage.used / 1024 ** 3),
            'percent': usage.percent
        }
    # print(f'{disk_parts=}')

    s_disk_io = psutil.disk_io_counters(perdisk=True)
    disk_io = [{
        'device': k,
        'read': round_half_up(s_disk_io[k].read_bytes / 1024 ** 3),
        'write': round_half_up(s_disk_io[k].write_bytes / 1024 ** 3),
    } for k in s_disk_io]
    # print(f'{disk_io=}')

    s_net_io = psutil.net_io_counters(pernic=True)
    net_io = [{
        'device': k,
        'send': round_half_up(s_net_io[k].bytes_sent / 1024 ** 3),
        'recv': round_half_up(s_net_io[k].bytes_recv / 1024 ** 3),
    } for k in s_net_io if is_physical_if(k)]
    # print(f'{net_io=}')

    if psutil.MACOS and not is_root():
        net_conn = None
    else:
        net_conn = {'count': len(psutil.net_connections())}

    # print(f'{net_conn=}')

    # print(psutil.sensors_temperatures())

    processes = {'count': len(psutil.pids())}
    # print(f'{processes=}')

    # print()
    return {
        'cpu': cpu,
        'memory': memory,
        'swap': swap,
        'disk_parts': disk_parts,
        'disk_io': disk_io,
        'net_io': net_io,
        'net_conn': net_conn,
        'processes': processes
    }


class App:
    def __init__(self):
        self.client = clickhouse_connect.get_client(host='8.134.13.200', username='default', database='monitor',
                                                    password='world')

    def save_machine_name(self):
        self.client.insert('machine', [(machine_name(), machine_uuid())], ('name', 'uuid'))

    def save(self, now_time: datetime, m_uuid: uuid.UUID, status: dict[str, dict | list]):
        for key, value in status.items():
            rows = []
            keys = []
            if isinstance(value, list) and len(value) > 0:
                keys = ['time', 'uuid'] + list(value[0].keys())
                for row in value:
                    rows.append([now_time, m_uuid] + list(row.values()))
            elif isinstance(value, dict):
                keys = ['time', 'uuid'] + list(value.keys())
                rows.append([now_time, machine_uuid()] + list(value.values()))

            if len(rows) > 0 and len(keys) > 0:
                self.client.insert(key, rows, keys)

    def run(self):
        self.save_machine_name()
        m_uuid = machine_uuid()

        while True:
            now_time = get_time()
            res = get_status()
            # print(res)
            print(now_time)

            self.save(now_time, m_uuid, res)
            time.sleep(1.5)


def main():
    while True:
        try:
            App().run()
        except Exception as exp:
            print(exp)
        time.sleep(10)


if __name__ == '__main__':
    main()
