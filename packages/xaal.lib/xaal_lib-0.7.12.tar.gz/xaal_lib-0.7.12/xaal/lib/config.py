# Default configuration

import os
import sys
import binascii
from configobj import ConfigObj

# Default settings
DEF_ADDR = "224.0.29.200"
DEF_PORT = 1236
DEF_HOPS = 10
DEF_ALIVE_TIMER = 100
DEF_CIPHER_WINDOW = 60 * 2
DEF_QUEUE_SIZE = 10
DEF_LOG_LEVEL = "DEBUG"
DEF_LOG_PATH = "/var/log/xaal"
DEF_REMOTE_CONSOLE = False


STACK_VERSION = 7


class Config:
    def __init__(self):
        self.conf_dir = os.environ.get("XAAL_CONF_DIR", os.path.expanduser("~/.xaal"))
        self.address = DEF_ADDR
        self.port = DEF_PORT
        self.hops = DEF_HOPS
        self.alive_timer = DEF_ALIVE_TIMER
        self.cipher_window = DEF_CIPHER_WINDOW
        self.queue_size = DEF_QUEUE_SIZE
        self.log_level = DEF_LOG_LEVEL
        self.log_path = DEF_LOG_PATH
        self.remote_console = DEF_REMOTE_CONSOLE
        self.key = b''
        self.STACK_VERSION = STACK_VERSION

    def load(self, name="xaal.ini"):
        filename = os.path.join(self.conf_dir, name)
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"Unable to load xAAL config file [{filename}]")

        cfg = ConfigObj(filename)
        self.address = self.safe_string(cfg.get('address'), DEF_ADDR)
        self.port = self.safe_int(cfg.get('port'), DEF_PORT)
        self.hops = self.safe_int(cfg.get('hops'), DEF_HOPS)
        self.alive_timer = self.safe_int(cfg.get('alive_timer'), DEF_ALIVE_TIMER)
        self.cipher_window = self.safe_int(cfg.get('cipher_window'), DEF_CIPHER_WINDOW)
        self.queue_size = self.safe_int(cfg.get('queue_size'), DEF_QUEUE_SIZE)
        self.log_level = self.safe_string(cfg.get('log_level'), DEF_LOG_LEVEL)
        self.log_path = self.safe_string(cfg.get('log_path'), DEF_LOG_PATH)
        self.remote_console = self.safe_bool(cfg.get('remote_console'), DEF_REMOTE_CONSOLE)

        key = cfg.get('key', None)
        if key and type(key) is str:
            self.key = binascii.unhexlify(key.encode('utf-8'))
        else:
            raise ValueError(f"Key not set in config file [{filename}]")

    ## Helper functions
    # Pylint enforce to sanity check the input. In fact, ConfigObj can do the job without issue
    # but Pytlint assume cfg.get can return None (even w/ default set), so it warm about wrong
    # type in all config setting. By doing this I insure that the value is of the right type.

    @staticmethod
    def safe_int(value, default):
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def safe_string(value, default):
        if value is None:
            return default
        try:
            return str(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def safe_bool(value, default):
        if value is None:
            return default
        if value.lower() == "true":
            return True
        return False


config_dir = os.environ.get("XAAL_CONF_DIR", None)
config = Config()

if config_dir is None or config_dir != '':
    try:
        config.load()
    except Exception as e:
        print(e)
        sys.exit(-1)
