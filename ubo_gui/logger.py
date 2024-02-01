# ruff: noqa: D100, D101, D102, D103, D104, D107
from __future__ import annotations

import logging
import sys

logger = logging.getLogger('ubo-gui')
logger.propagate = False


class ExtraFormatter(logging.Formatter):
    def_keys = (
        'name',
        'msg',
        'args',
        'levelname',
        'levelno',
        'pathname',
        'filename',
        'module',
        'exc_info',
        'exc_text',
        'stack_info',
        'lineno',
        'funcName',
        'created',
        'msecs',
        'relativeCreated',
        'thread',
        'threadName',
        'processName',
        'process',
        'message',
    )

    def format(self: ExtraFormatter, record: logging.LogRecord) -> str:
        string = super().format(record)
        extra = {k: v for k, v in record.__dict__.items() if k not in self.def_keys}
        if len(extra) > 0:
            string += ' - extra: ' + str(extra)

        return string


def add_stdout_handler(level: int = logging.DEBUG) -> None:
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(level)
    stdout_handler.setFormatter(
        ExtraFormatter(
            '%(created)f [%(levelname)s] %(message)s',
            '%Y-%m-%d %H:%M:%S',
        ),
    )
    logger.addHandler(stdout_handler)


def add_file_handler(level: int = logging.DEBUG) -> None:
    file_handler = logging.FileHandler('ubo-gui.log')
    file_handler.setLevel(level)
    file_handler.setFormatter(
        ExtraFormatter(
            '%(created)f [%(levelname)s] %(message)s',
            '%Y-%m-%d %H:%M:%S',
        ),
    )
    logger.addHandler(file_handler)


__all__ = ('logger', 'add_stdout_handler', 'add_file_handler')
