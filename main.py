import re
import time
from datetime import datetime
from decimal import Decimal
from typing import Iterable

import clickhouse_connect
import psutil


def round_half_up(value: float, exp: str = '0.01'):
    return float(Decimal(value).quantize(Decimal(exp), rounding="ROUND_HALF_UP"))


client = clickhouse_connect.get_client(host='localhost', username='default', database='monitor', password='world')


def is_physical_if(name: str) -> bool:
    if 'prog_s' not in is_physical_if.__dict__:
        prog_s = []
        prefixes = ['en', 'wlan']
        for prefix in prefixes:
            p = re.compile(rf'{prefix}\d+')
            prog_s.append(p)
        is_physical_if.__dict__['prog_s'] = prog_s

    for prog in is_physical_if.__dict__['prog_s']:
        if prog.match(name) is not None:
            return True

    return False


def get_status():
    now_time = datetime.now()
    # print(f'time={now_time}')

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
        'used': round_half_up((s_vmem.total - s_vmem.available) / 1024 ** 3)
    }
    # print(f'{memory=}')

    s_swap = psutil.swap_memory()
    swap = {
        'total': round_half_up(s_swap.total / 1024 ** 3),
        'used': round_half_up(s_swap.used / 1024 ** 3),
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
            'used': round_half_up(usage.used / 1024 ** 3)
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

    # net_conn = len(psutil.net_connections())
    # print(f'{net_conn=}')

    # print(psutil.sensors_temperatures()) //todo

    # print()
    return {
        'time': now_time,
        'cpu': cpu,
        'memory': memory,
        'swap': swap,
        'disk_parts': disk_parts,
        'disk_io': disk_io,
        'net_io': net_io
    }


def save(status: dict[str, dict | list]):
    cpu_rows = []
    for cpu in status['cpu']:
        cpu_rows.append([status['time']] + list(cpu.values()))
    client.insert('cpu', cpu_rows, ['time'] + list(status['cpu'][0].keys()))

    client.insert('memory', [[status['time']] + list(status['memory'].values())],
                  ['time'] + list(status['memory'].keys()))

    client.insert('swap', [[status['time']] + list(status['swap'].values())],
                  ['time'] + list(status['swap'].keys()))

    disk_parts_rows = []
    for part in status['disk_parts']:
        disk_parts_rows.append([status['time']] + list(part.values()))
    client.insert('disk_parts', disk_parts_rows, ['time'] + list(status['disk_parts'][0].keys()))

    disk_io_rows = []
    for disk in status['disk_io']:
        disk_io_rows.append([status['time']] + list(disk.values()))
    client.insert('disk_io', disk_io_rows, ['time'] + list(status['disk_io'][0].keys()))

    net_io_rows = []
    for net in status['net_io']:
        net_io_rows.append([status['time']] + list(net.values()))
    client.insert('net_io', net_io_rows, ['time'] + list(status['net_io'][0].keys()))


def main():
    for i in range(3):
        res = get_status()
        print(res)

        save(res)
        time.sleep(1)


if __name__ == '__main__':
    main()
