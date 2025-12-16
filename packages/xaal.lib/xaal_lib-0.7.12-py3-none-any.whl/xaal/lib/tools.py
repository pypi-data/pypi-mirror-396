#
#  Copyright 2014, Jérôme Colin, Jérôme Kerdreux, Philippe Tanguy,
#  Telecom Bretagne.
#
#  This file is part of xAAL.
#
#  xAAL is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  xAAL is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with xAAL. If not, see <http://www.gnu.org/licenses/>.
#

import functools
import os
import re
import sys
from typing import Optional, Union

import pysodium
from configobj import ConfigObj

from .config import config
from .bindings import UUID

XAAL_DEVTYPE_PATTERN = "^[a-zA-Z][a-zA-Z0-9_-]*\\.[a-zA-Z][a-zA-Z0-9_-]*$"


def get_cfg_filename(name: str, cfg_dir: str = config.conf_dir) -> str:
    if name.startswith("xaal."):
        name = name[5:]
    filename = "%s.ini" % name
    if not os.path.isdir(cfg_dir):
        print("Your configuration directory doesn't exist: [%s]" % cfg_dir)
    return os.path.join(cfg_dir, filename)


def load_cfg_file(filename: str) -> Optional[ConfigObj]:
    """load .ini file and return it as dict"""
    if os.path.isfile(filename):
        return ConfigObj(filename, indent_type="  ", encoding='utf8')
    return None


def load_cfg(app_name: str) -> Optional[ConfigObj]:
    filename = get_cfg_filename(app_name)
    return load_cfg_file(filename)


def load_cfg_or_die(app_name: str) -> ConfigObj:
    cfg = load_cfg(app_name)
    if not cfg:
        print("Unable to load config file %s" % get_cfg_filename(app_name))
        sys.exit(-1)
    return cfg


def new_cfg(app_name: str) -> ConfigObj:
    filename = get_cfg_filename(app_name)
    cfg = ConfigObj(filename, indent_type="  ")
    cfg['config'] = {'addr' : get_random_uuid().str}
    return cfg


def get_random_uuid() -> UUID:
    return UUID.random()


def get_random_base_uuid(digit=2) -> UUID:
    return UUID.random_base(digit)


def get_uuid(val: Union[UUID, str]) -> Optional[UUID]:
    if isinstance(val, UUID):
        return val
    if isinstance(val, str):
        return str_to_uuid(val)
    return None


def str_to_uuid(val: str) -> Optional[UUID]:
    """return an xAAL address for a given string"""
    try:
        return UUID(val)
    except ValueError:
        return None


def bytes_to_uuid(val: bytes) -> Optional[UUID]:
    try:
        return UUID(bytes=val)
    except ValueError:
        return None


def is_valid_uuid(val: UUID) -> bool:
    return isinstance(val, UUID)


def is_valid_address(val: UUID) -> bool:
    return is_valid_uuid(val)


@functools.lru_cache(maxsize=128)
def is_valid_dev_type(val: str) -> bool:
    if not isinstance(val, str):
        return False
    if re.match(XAAL_DEVTYPE_PATTERN, val):
        return True
    return False


def pass2key(passphrase: str) -> bytes:
    """Generate key from passphrase using libsodium
    crypto_pwhash_scryptsalsa208sha256 func
    salt: buffer of zeros
    opslimit: crypto_pwhash_scryptsalsa208sha256_OPSLIMIT_INTERACTIVE
    memlimit: crypto_pwhash_scryptsalsa208sha256_MEMLIMIT_INTERACTIVE
    """
    buf = passphrase.encode("utf-8")
    KEY_BYTES = pysodium.crypto_pwhash_scryptsalsa208sha256_SALTBYTES  # 32
    # this should be:
    # salt = bytes(KEY_BYTES)
    # but due to bytes() stupid stuff in py2 we need this awfull stuff
    salt = ('\00' * KEY_BYTES).encode('utf-8')
    opslimit = pysodium.crypto_pwhash_scryptsalsa208sha256_OPSLIMIT_INTERACTIVE
    memlimit = pysodium.crypto_pwhash_scryptsalsa208sha256_MEMLIMIT_INTERACTIVE
    key = pysodium.crypto_pwhash_scryptsalsa208sha256(KEY_BYTES, buf, salt, opslimit, memlimit)
    return key


@functools.lru_cache(maxsize=128)
def reduce_addr(addr: UUID) -> str:
    """return a string based addred without all  digits"""
    tmp = addr.str
    return tmp[:5] + '..' + tmp[-5:]
