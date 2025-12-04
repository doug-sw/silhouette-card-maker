import re
from types import SimpleNamespace

def remove_nonalphanumeric(s: str) -> str:
    return re.sub(r'[^\w]', '', s)


def to_namespace(obj):
    if isinstance(obj, dict):
        return SimpleNamespace(**{k: to_namespace(v) for k, v in obj.items()})
    elif isinstance(obj, list):
        return [to_namespace(v) for v in obj]
    else:
        return obj
