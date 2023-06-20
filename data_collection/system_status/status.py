import time
from datetime import datetime
from typing import Iterable

import psutil

from ..utils import *

last_s_disk_io = None
last_s_net_io = None


def now_time():
    return datetime.now()


def cpu():
    s_cpu = psutil.cpu_percent(interval=None, percpu=True)
    if not isinstance(s_cpu, Iterable):
        s_cpu = [s_cpu]
    return [{
        'core': i,
        'percent': s_cpu[i]
    } for i in range(psutil.cpu_count())]


def memory():
    s_vmem = psutil.virtual_memory()
    return {
        'total': round_half_up(s_vmem.total / 1024 ** 3),
        'used': round_half_up((s_vmem.total - s_vmem.available) / 1024 ** 3),
        'percent': s_vmem.percent
    }


def swap():
    s_swap = psutil.swap_memory()
    return {
        'total': round_half_up(s_swap.total / 1024 ** 3),
        'used': round_half_up(s_swap.used / 1024 ** 3),
        'percent': s_swap.percent
    }


def disk_parts():
    s_disk_part = psutil.disk_partitions()
    parts = [{
        'device': p.device,
        'mountpoint': p.mountpoint,
    } for p in s_disk_part]
    for p in parts:
        usage = psutil.disk_usage(p['mountpoint'])
        p |= {
            'total': round_half_up(usage.total / 1024 ** 3),
            'used': round_half_up(usage.used / 1024 ** 3),
            'percent': usage.percent
        }
    return parts


def disk_io():
    s_disk_io = psutil.disk_io_counters(perdisk=True)
    global last_s_disk_io
    if last_s_disk_io is None:
        last_s_disk_io = s_disk_io
    io_info = [{
        'device': k,
        'read': round_half_up((s_disk_io[k].read_bytes - last_s_disk_io[k].read_bytes) / 1024 ** 2),
        'write': round_half_up((s_disk_io[k].write_bytes - last_s_disk_io[k].write_bytes) / 1024 ** 2),
    } for k in s_disk_io]
    last_s_disk_io = s_disk_io
    return io_info


def net_io():
    s_net_io = psutil.net_io_counters(pernic=True)
    global last_s_net_io
    if last_s_net_io is None:
        last_s_net_io = s_net_io
    return [{
        'device': k,
        'send': round_half_up((s_net_io[k].bytes_sent - last_s_net_io[k].bytes_sent) / 1024 ** 2),
        'recv': round_half_up((s_net_io[k].bytes_recv - last_s_net_io[k].bytes_recv) / 1024 ** 2),
    } for k in s_net_io if is_physical_if(k)]


def init():
    cpu()
    disk_io()
    net_io()


def test():
    init()
    time.sleep(1.5)
    print(now_time())
    print(cpu())
    print(memory())
    print(swap())
    print(disk_parts())
    print(disk_io())
    print(net_io())


if __name__ == '__main__':
    test()
