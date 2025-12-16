from . helpers import *
from decorator import decorator
import asyncio
import logging

@decorator
def spawn(func, *args, **kwargs):
    return asyncio.get_event_loop().run_in_executor(None, func, *args, **kwargs)


def static_vars(**kwargs_):
    def decorate(func):
        for k in kwargs_:
            setattr(func, k, kwargs_[k])
        return func
    return decorate


def run_async_package(pkg_name, pkg_setup, console_log=True, file_log=False):
    if console_log:
        set_console_title(pkg_name)
        setup_console_logger()
    if file_log:
        setup_file_logger(pkg_name)

    from .aioengine import AsyncEngine
    eng = AsyncEngine()
    eng.start()
    logger = logging.getLogger(pkg_name)
    logger.info("starting xaal package: %s"% pkg_name )
    result = pkg_setup(eng)
    if result is not True:
        logger.critical("something goes wrong with package: %s" % pkg_name)
    try:
        eng.run()
    except KeyboardInterrupt:
        eng.shutdown()
        logger.info("Exit")
