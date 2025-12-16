"""
This file contains some helpers functions. This functions aren't used in the lib itself
but can be usefull for xaal packages developpers
"""

import logging
import logging.handlers
import os
import time
from typing import Any, Optional, Union

import coloredlogs
from decorator import decorator

from .config import config


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@decorator
def timeit(method, *args, **kwargs):
    logger = logging.getLogger(__name__)
    ts = time.time()
    result = method(*args, **kwargs)
    te = time.time()
    logger.debug("%r (%r, %r) %2.6f sec" % (method.__name__, args, kwargs, te - ts))
    return result


def set_console_title(value: str):
    # set xterm title
    print("\x1b]0;xAAL => %s\x07" % value, end="\r")


def setup_console_logger(level: Union[str, int] = config.log_level):
    # fmt = "%(asctime)s %(name)-25s %(funcName)-18s %(levelname)-8s %(message)s"
    fmt = "%(asctime)s %(name)-25s %(funcName)-18s %(message)s"
    # fmt = '[%(name)s] %(funcName)s %(levelname)s: %(message)s'
    coloredlogs.install(level=level, fmt=fmt)


def setup_file_logger(name: str, level: Union[str, int] = config.log_level, filename: Optional[str] = None):
    filename = filename or os.path.join(config.log_path, "%s.log" % name)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    handler = logging.handlers.RotatingFileHandler(filename, "a", 10000, 1, "utf8")
    handler.setLevel(level)
    handler.setFormatter(formatter)
    # register the new handler
    logger = logging.getLogger(name)
    logger.root.addHandler(handler)
    logger.root.setLevel('DEBUG')


# ---------------------------------------------------------------------------
# TBD: We should merge this stuffs, and add support for default config file
#      and commnand line parsing.
#
# Default arguments console_log and file_log are (and should) never be used.
# ---------------------------------------------------------------------------
def run_package(pkg_name: str, pkg_setup: Any, console_log: bool = True, file_log: bool = False):
    if console_log:
        set_console_title(pkg_name)
        setup_console_logger()
    if file_log:
        setup_file_logger(pkg_name)
    logger = logging.getLogger(pkg_name)
    logger.info("starting xaal package: %s" % pkg_name)

    from .engine import Engine

    eng = Engine()
    result = pkg_setup(eng)

    if result is not True:
        logger.critical("something goes wrong with package: %s" % pkg_name)
    try:
        eng.run()
    except KeyboardInterrupt:
        eng.shutdown()
        logger.info("exit")


__all__ = ['singleton', 'timeit', 'set_console_title', 'setup_console_logger', 'setup_file_logger', 'run_package']
