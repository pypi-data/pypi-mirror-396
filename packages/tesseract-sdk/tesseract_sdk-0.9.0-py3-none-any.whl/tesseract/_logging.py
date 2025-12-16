"""
Code is from https://github.com/complyue/python-bunyan, but this project is not longer maintained and we do
not want to take over maintenance ownership from the original.

Original MIT License:

The MIT License (MIT)

Copyright (c) 2016 Uphold INC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import datetime
import json
import logging
import socket
import traceback


from typing import List, Callable, Any
from inspect import istraceback
from collections import OrderedDict


def object_startswith(key: str, value: str) -> bool:
    return hasattr(key, "startswith") and key.startswith(value)


def merge_record_extra(
    record: logging.LogRecord, target: dict, reserved: List[str] = []
) -> dict:
    """
    Merges extra attributes from LogRecord object into target dictionary.

    Args:
        record: a log record
        target dict to update
        reserved: dict or list with reserved keys to skip
    """

    new_values = {
        key: value
        for key, value in record.__dict__.items()
        if (key not in reserved and not object_startswith(key, "_"))
    }

    target.update(new_values)

    return target


def get_json_handler(datefmt: str) -> Callable:
    def handler(obj: Any):
        if isinstance(obj, datetime.datetime):
            if obj.year < 1900:
                # strftime do not work with date < 1900
                return obj.isoformat()
            return obj.strftime(datefmt or "%Y-%m-%dT%H:%M")

        elif isinstance(obj, datetime.date):
            return obj.isoformat()

        elif isinstance(obj, datetime.time):
            return obj.strftime("%H:%M")

        elif istraceback(obj):
            tb = "".join(traceback.format_tb(obj))
            return tb.strip()

        elif isinstance(obj, Exception):
            return "Exception: %s" % str(obj)

        return str(obj)

    return handler


class BunyanFormatter(logging.Formatter):
    """Bunyan log formatter.

    Implements a logging Formatter by extending jsonlogger.JsonFormatter
    to use bunyan's standard names and values.
    """

    def __init__(self, *args, **kwargs):
        """
        Defined default log format.
        """
        self._required_fields = [
            "asctime",
            "exc_info",
            "levelno",
            "message",
            "name",
            "process",
        ]

        self._skip_fields = self._required_fields[:]
        self._skip_fields += [
            "args",
            "created",
            "exc_text",
            "filename",
            "funcName",
            "levelname",
            "lineno",
            "module",
            "msecs",
            "pathname",
            "processName",
            "relativeCreated",
            "stack_info",
            "thread",
            "threadName",
        ]

        def log_format(x: List[Any]):
            return ["%({0:s})".format(i) for i in x]

        super().__init__(
            " ".join(log_format(self._required_fields)),
            "%Y-%m-%dT%H:%M:%SZ",
            *args,
            **kwargs,
        )
        self.json_default = get_json_handler(self.datefmt)

    def add_fields(
        self, log_record: dict, record: logging.LogRecord, message_dict: dict
    ):
        """
        Override this method to implement custom logic for adding fields.
        """
        for field in self._required_fields:
            log_record[field] = record.__dict__.get(field)

        log_record.update(message_dict)
        merge_record_extra(record, log_record, reserved=self._skip_fields)

    def jsonify_log_record(self, log_record):
        """
        Returns a json string of the log record.
        """
        return json.dumps(log_record, default=self.json_default, allow_nan=True)

    def format(self, record):
        """
        Formats a log record and serializes to json
        """
        message_dict = {}

        if isinstance(record.msg, dict):
            message_dict = record.msg

            if len(record.args) == 1 and isinstance(record.args[0], str):
                # bunyan style log method: fields object + msg string
                record.msg = record.args[0]
                record.message = record.args[0] % message_dict
            else:
                record.message = None

        else:
            record.message = record.getMessage()

        # only format time if needed
        if "asctime" in self._required_fields:
            record.time = self.formatTime(record, self.datefmt)

        # Display formatted exception, but allow overriding it in the
        # user-supplied dict.
        if record.exc_info and not message_dict.get("exc_info"):
            message_dict["exc_info"] = self.formatException(record.exc_info)

        log_record = OrderedDict()

        self.add_fields(log_record, record, message_dict)
        log_record = self.process_log_record(log_record)

        return self.jsonify_log_record(log_record)

    def process_log_record(self, log_record):
        """
        Bunyanize log_record:
          - Renames python's standard names by bunyan's.
          - Add hostname and version (v).
          - Normalize level (+10).
        """
        # Add hostname
        log_record["hostname"] = socket.gethostname()
        log_record["level"] = log_record["levelno"] + 10

        if "message" in log_record and log_record["message"]:
            log_record["msg"] = log_record["message"]
        else:
            log_record["msg"] = ""

        log_record["pid"] = log_record["process"]
        log_record["v"] = 0

        if not log_record["exc_info"]:
            del log_record["exc_info"]

        del log_record["asctime"]
        del log_record["levelno"]
        del log_record["message"]
        del log_record["process"]

        return log_record


def _get_level():
    log_level = os.getenv("LOG_LEVEL")

    level = logging.INFO
    try:
        level = getattr(logging, log_level.upper())
    except Exception:
        pass

    return level


def _get_logger(name: str, outfile: str = None):
    logger = logging.getLogger(name)
    level = _get_level()
    logger.handlers = []
    logger.propagate = False

    stderr_log_handler = logging.StreamHandler()
    stderr_log_handler.setLevel(level)
    stderr_log_handler.setFormatter(BunyanFormatter())
    logger.addHandler(stderr_log_handler)

    if outfile is not None:
        file_log_handler = logging.FileHandler(outfile)
        file_log_handler.setLevel(level)
        file_log_handler.setFormatter(BunyanFormatter())
        logger.addHandler(file_log_handler)

    logger.setLevel(_get_level())

    return logger


def _child_logger(logger: logging.Logger, name: str, outfile: str):
    logger = logger.getChild(name)
    level = _get_level()

    file_log_handler = logging.FileHandler(outfile)
    file_log_handler.setLevel(level)
    file_log_handler.setFormatter(BunyanFormatter())
    logger.addHandler(file_log_handler)

    return logger
