import time
from decimal import Decimal
from typing import Iterable

import psutil


def round_half_up(value: float, exp: str = '1.0'):
    return float(Decimal(value).quantize(Decimal(exp), rounding="ROUND_HALF_UP"))


def status():
    s_cpu = psutil.cpu_percent(interval=None, percpu=True)
    if not isinstance(s_cpu, Iterable):
        s_cpu = [s_cpu]
    cpu = dict(zip(range(psutil.cpu_count()), s_cpu))
    print(f'{cpu=}')

    s_vmem = psutil.virtual_memory()
    memory = {
        'total': round_half_up(s_vmem.total / 1024 ** 3),
        'used': round_half_up((s_vmem.total - s_vmem.available) / 1024 ** 3)
    }
    print(f'{memory=}')

    s_swap = psutil.swap_memory()
    swap = {
        'total': round_half_up(s_swap.total / 1024 ** 3),
        'used': round_half_up(s_swap.used / 1024 ** 3),
    }
    print(f'{swap=}')

    s_disk_part = psutil.disk_partitions()
    parts = [{
        'device': p.device,
        'mountpoint': p.mountpoint,
    } for p in s_disk_part]
    for p in parts:
        usage = psutil.disk_usage(p['device'])
        p |= {
            'total': usage.total,
            'used': usage.used,
        }
    print(f'{parts=}')

    s_disk_io = psutil.disk_io_counters(perdisk=True)
    disk_io = [{
        'device': k,
        'read': round_half_up(s_disk_io[k].read_bytes / 1024 ** 2, '0.01'),
        'write': round_half_up(s_disk_io[k].write_bytes / 1024 ** 2, '0.01'),
    } for k in s_disk_io]
    print(f'{disk_io=}')

    s_net_io = psutil.net_io_counters(pernic=True)
    net_io = [{
        'device': k,
        'send': round_half_up(s_net_io[k].bytes_sent / 1024 ** 2, '0.01'),
        'recv': round_half_up(s_net_io[k].bytes_recv / 1024 ** 2, '0.01'),
    } for k in s_net_io]
    print(f'{net_io=}')

    # net_conn = len(psutil.net_connections())
    # print(f'{net_conn=}')

    # print(psutil.sensors_temperatures()) //todo

    print()


def main():
    for i in range(3):
        status()
        time.sleep(1)


if __name__ == '__main__':
    main()
