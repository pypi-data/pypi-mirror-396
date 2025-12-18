import datetime
import os
import random
import time
import uuid
from hashlib import md5
from itertools import chain

from django.core.handlers.wsgi import WSGIRequest


def uniq_id(with_time=True) -> str:
    """
    Create Uniq ID
    """

    _md5 = md5()
    _md5.update(str(int(time.time() * 1000)).encode())
    time_str = str(_md5.hexdigest())
    uniq = str(uuid.uuid5(uuid.uuid1(), uuid.uuid4().hex).hex)
    return f"{time_str if with_time else ''}{uniq}"


def uniq_id_without_time() -> str:
    """
    Create Uniq ID
    """

    return uniq_id(False)


def simple_uniq_id(length: int) -> str:
    """
    Create Simple Uniq ID
    """

    base = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"
    random.seed(uniq_id())
    uniq = ""
    i = 0
    while i < length:
        i += 1
        uniq += base[random.randint(0, len(base) - 1)]
    return uniq


def num_code(length: int) -> str:
    """
    Create Number Code
    """

    random.seed(uniq_id())
    uniq = ""
    i = 0
    while i < length:
        i += 1
        uniq += str(random.randint(0, 9))
    return uniq


def get_ip(request: WSGIRequest) -> str:
    """
    Get IP from Request
    """

    if request.META.get("HTTP_X_REAL_IP"):
        return request.META.get("HTTP_X_REAL_IP")
    if request.META.get("HTTP_X_FORWARDED_FOR"):
        return request.META.get("HTTP_X_FORWARDED_FOR").replace(" ", "").split(",")[0]
    if request.META.get("HTTP_X_FORWARD_FOR"):
        return request.META.get("HTTP_X_FORWARD_FOR").replace(" ", "").split(",")[0]
    return request.META.get("REMOTE_ADDR")


def field_handler(data) -> any:
    """
    Handler Date/Datetime Field Data
    """

    if isinstance(data, datetime.datetime):
        return data.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(data, datetime.date):
        return data.strftime("%Y-%m-%d")
    return data


def model_to_dict(instance, fields=None, exclude=None) -> dict:
    """
    Trans Model Data to Json
    """

    opts = instance._meta  # pylint: disable=W0212
    data = {}
    for _field in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
        if fields is not None and _field.name not in fields:
            continue
        if exclude and _field.name in exclude:
            continue
        data[_field.name] = field_handler(_field.value_from_object(instance))
    return data


def getenv_or_raise(key: str) -> str:
    """
    Force Get Env
    """

    val = os.getenv(key)
    if val is None:
        raise ValueError(f"Env Not Set, Key [{key}]")
    return val


def strtobool(val):
    """
    Trans Str to Bool
    """

    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True
    if val in ("n", "no", "f", "false", "off", "0"):
        return False
    raise ValueError(f"invalid truth value {val}")


def get_md5(content):
    """
    Get Dict List MD5
    """

    if isinstance(content, dict):
        return get_md5([(str(k), get_md5(content[k])) for k in sorted(content.keys())])

    if isinstance(content, (list, tuple)):
        content = sorted(get_md5(k) for k in content)

    content = str(content)
    _md5 = md5()
    if isinstance(content, str):
        _md5.update(content.encode("utf8"))
    else:
        _md5.update(content)
    return _md5.hexdigest()
