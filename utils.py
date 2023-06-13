import platform
import uuid

import psutil


def bytes2human(n):
    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.8K'
    # >>> bytes2human(100001221)
    # '95.4M'
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if abs(n) >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n


def machine_name() -> str:
    if 's_machine_name' not in machine_name.__dict__:
        machine_name.__dict__['s_machine_name'] = platform.node()
    return machine_name.__dict__['s_machine_name']


def machine_uuid() -> str:
    if 's_machine_uuid' not in machine_uuid.__dict__:
        machine_uuid.__dict__['s_machine_uuid'] = str(uuid.UUID(int=uuid.getnode()))
    return machine_uuid.__dict__['s_machine_uuid']
