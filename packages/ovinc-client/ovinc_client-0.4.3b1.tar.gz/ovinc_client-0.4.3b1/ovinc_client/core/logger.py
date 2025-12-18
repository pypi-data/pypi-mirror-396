import datetime
import json
import logging
import sys

from django.utils.encoding import force_str


def get_logging_config_dict(*, log_level: str, log_format: str = "json") -> dict:
    """
    Get Logging Config
    """

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": (
                {
                    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "fmt": (
                        "%(levelname)s %(asctime)s %(pathname)s %(lineno)d "
                        "%(funcName)s %(process)d %(thread)d %(message)s"
                    ),
                }
                if log_format == "json"
                else {
                    "format": (
                        "%(levelname)s [%(asctime)s] %(pathname)s " "%(lineno)d %(funcName)s " "\n \t %(message)s \n"
                    ),
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            ),
        },
        "handlers": {
            "stream": {
                "level": log_level,
                "class": "logging.StreamHandler",
                "formatter": "verbose",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            "root": {"handlers": ["stream"], "level": log_level, "propagate": False},
            "app": {"handlers": ["stream"], "level": log_level, "propagate": False},
            "mysql": {"handlers": ["stream"], "level": log_level, "propagate": False},
            "cel": {"handlers": ["stream"], "level": log_level, "propagate": False},
        },
    }


class DumpLog:
    """
    Dump Log to Str
    """

    def __init__(self, *args):
        self._args = args

    @property
    def args(self) -> tuple:
        new_args = []
        for _arg in self._args:
            try:
                match _arg:
                    case bytes():
                        new_args.append(_arg.decode())
                    case str() | int():
                        new_args.append(_arg)
                    case datetime.datetime() | datetime.date():
                        new_args.append(str(_arg))
                    case Exception():
                        new_args.append(f"{_arg} => {_arg.__dict__}")
                    case _:
                        new_args.append(json.dumps(_arg, ensure_ascii=False))
            except Exception:  # pylint: disable=W0718
                new_args.append(force_str(_arg))
        return tuple(new_args)


class LogLevelHandler:
    """
    Handler Log Level
    """

    def __init__(self, log, level: str):
        self.log = log
        self.level = level

    def __call__(self, msg, *args):
        args = DumpLog(*args).args
        func = getattr(self.log.logger, self.level)
        func(msg, *args)


class Log:
    """
    Log
    """

    def __init__(self, name):
        self.logger = logging.getLogger(name)

    def __getattr__(self, level: str):
        return LogLevelHandler(self, level)


logger = Log("app")
celery_logger = Log("cel")
mysql_logger = Log("mysql")
