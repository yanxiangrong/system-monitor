import os
import platform
import re
import uuid
from decimal import Decimal


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


def machine_uuid() -> uuid.UUID:
    if 's_machine_uuid' not in machine_uuid.__dict__:
        machine_uuid.__dict__['s_machine_uuid'] = uuid.UUID(int=uuid.getnode())
    return machine_uuid.__dict__['s_machine_uuid']


def is_root():
    return os.geteuid() == 0


def is_physical_if(name: str) -> bool:
    if 'prog_s' not in is_physical_if.__dict__:
        prog_s = []
        prefixes = ['en', 'wlan', 'WLAN', '以太网']
        for prefix in prefixes:
            p = re.compile(rf'{prefix}\d*')
            prog_s.append(p)
        is_physical_if.__dict__['prog_s'] = prog_s

    for prog in is_physical_if.__dict__['prog_s']:
        if prog.match(name) is not None:
            return True

    return False


def round_half_up(value: float, exp: str = '0.01'):
    return float(Decimal(value).quantize(Decimal(exp), rounding="ROUND_HALF_UP"))
