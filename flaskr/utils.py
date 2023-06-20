import json
from datetime import datetime
from typing import Iterable


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return str(obj)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


def to_json(obj) -> str:
    return json.dumps(obj, cls=ComplexEncoder)
