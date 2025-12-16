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

import logging
import time
import typing
from typing import Any, Optional, Union, Callable, Awaitable, Dict

from tabulate import tabulate

from . import bindings, config, tools
from .exceptions import DeviceError

if typing.TYPE_CHECKING:
    from .aioengine import AsyncEngine
    from .engine import Engine
    from .core import EngineMixin

# Funtion types with any arguments and return a dict or None (device methods)
MethodT = Union[Callable[..., Union[dict, None]], Callable[..., Awaitable[Union[dict, None]]]]

logger = logging.getLogger(__name__)


class Attribute(object):
    def __init__(self, name, dev: Optional['Device'] = None, default: Any = None):
        self.name = name
        self.default = default
        self.device: Optional['Device'] = dev
        self.__value = default

    @property
    def value(self) -> Any:
        return self.__value

    @value.setter
    def value(self, value: Any):
        if value != self.__value and self.device:
            eng = self.device.engine
            if eng:
                eng.add_attributes_change(self)
                logger.debug("Attr change %s %s=%s" % (self.device.address, self.name, value))
        self.__value = value

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{self.__module__}.Attribute {self.name} at 0x{id(self):x}>"


class Attributes(list):
    """Devices owns a attributes list. This list also have dict-like access"""

    def __getitem__(self, value):
        if isinstance(value, int):
            return list.__getitem__(self, value)
        for k in self:
            if value == k.name:
                return k.value
        raise KeyError(value)

    def __setitem__(self, name, value):
        if isinstance(name, int):
            return list.__setitem__(self, name, value)
        for k in self:
            if name == k.name:
                k.value = value
                return
        raise KeyError(name)


class Device(object):
    __slots__ = [
        '__dev_type',
        '__address',
        'group_id',
        'vendor_id',
        'product_id',
        'hw_id',
        '__version',
        '__url',
        'schema',
        'info',
        'unsupported_attributes',
        'unsupported_methods',
        'unsupported_notifications',
        'alive_period',
        'next_alive',
        '__attributes',
        'methods',
        'engine',
    ]

    def __init__(
        self,
        dev_type: str,
        addr: Optional[bindings.UUID] = None,
        engine: Union['AsyncEngine', 'Engine', 'EngineMixin', None] = None,
    ):
        # xAAL internal attributes for a device
        self.dev_type = dev_type  # xaal dev_type
        self.address = addr  # xaal addr
        self.group_id: Optional[bindings.UUID] = None  # group devices
        self.vendor_id: Optional[str] = None  # vendor ID ie : ACME
        self.product_id: Optional[str] = None  # product ID
        self.hw_id: Optional[str] = None  # hardware info
        self.version = None  # product release
        self.url = None  # product URL
        self.schema: Optional[str] = None  # schema URL
        self.info: Optional[str] = None  # additionnal info

        # Unsupported stuffs
        self.unsupported_attributes = []
        self.unsupported_methods = []
        self.unsupported_notifications = []
        # Alive management
        self.alive_period = config.alive_timer  # time in sec between two alive
        self.next_alive = 0
        # Default attributes & methods
        self.__attributes = Attributes()
        self.methods: Dict[str, MethodT] = {
            'get_attributes': self._get_attributes,
            'get_description': self._get_description,
        }
        self.engine = engine

    @property
    def dev_type(self) -> str:
        return self.__dev_type

    @dev_type.setter
    def dev_type(self, value: str):
        if not tools.is_valid_dev_type(value):
            raise DeviceError(f"The dev_type {value} is not valid")
        self.__dev_type = value

    @property
    def version(self) -> Optional[str]:
        return self.__version

    @version.setter
    def version(self, value: Any):
        # version must be a string
        if value:
            self.__version = "%s" % value
        else:
            self.__version = None

    @property
    def address(self) -> Optional[bindings.UUID]:
        return self.__address

    @address.setter
    def address(self, value: Optional[bindings.UUID]):
        if value is None:
            self.__address = None
            return
        if not tools.is_valid_address(value):
            raise DeviceError("This address is not valid")
        self.__address = value

    @property
    def url(self) -> Optional[bindings.URL]:
        return self.__url

    @url.setter
    def url(self, value: Optional[str]):
        if value is None:
            self.__url = None
        else:
            self.__url = bindings.URL(value)

    # attributes
    def new_attribute(self, name: str, default: Any = None):
        attr = Attribute(name, self, default)
        self.add_attribute(attr)
        return attr

    def add_attribute(self, attr: Attribute):
        if attr:
            self.__attributes.append(attr)
            attr.device = self

    def del_attribute(self, attr: Attribute):
        if attr:
            attr.device = None
            self.__attributes.remove(attr)

    def get_attribute(self, name: str) -> Optional[Attribute]:
        for attr in self.__attributes:
            if attr.name == name:
                return attr
        return None

    @property
    def attributes(self) -> Attributes:
        return self.__attributes

    @attributes.setter
    def attributes(self, values: Attributes):
        if isinstance(values, Attributes):
            self.__attributes = values
        else:
            raise DeviceError("Invalid attributes list, use class Attributes)")

    def add_method(self, name: str, func: MethodT):
        self.methods.update({name: func})

    def del_method(self, name: str):
        if name in self.methods:
            del self.methods[name]

    def get_methods(self) -> Dict[str, MethodT]:
        return self.methods

    def update_alive(self):
        """update the alive timimg"""
        self.next_alive = time.time() + self.alive_period

    def get_timeout(self) -> int:
        """return Alive timeout used for isAlive msg"""
        return 2 * self.alive_period

    #####################################################
    # Usefull methods
    #####################################################
    def dump(self):
        print("= Device: %s" % self)
        # info & description
        r = []
        r.append(['dev_type', self.dev_type])
        r.append(['address', self.address])
        for k, v in self._get_description().items():
            r.append([k, v])
        print(tabulate(r, tablefmt='psql'))

        # attributes
        if len(self._get_attributes()) > 0:
            r = []
            for k, v in self._get_attributes().items():
                r.append([k, str(v)])
            print(tabulate(r, tablefmt='psql'))

        # methods
        if len(self.methods) > 0:
            r = []
            for k, v in self.methods.items():
                r.append([k, v.__name__])
            print(tabulate(r, tablefmt='psql'))

    def __repr__(self) -> str:
        return f"<xaal.Device {id(self):x} {self.address} {self.dev_type}>"

    #####################################################
    # default public methods
    #####################################################
    def _get_description(self) -> dict:
        result = {}
        if self.vendor_id:
            result['vendor_id'] = self.vendor_id
        if self.product_id:
            result['product_id'] = self.product_id
        if self.version:
            result['version'] = self.version
        if self.url:
            result['url'] = self.url
        if self.schema:
            result['schema'] = self.schema
        if self.info:
            result['info'] = self.info
        if self.hw_id:
            result['hw_id'] = self.hw_id
        if self.group_id:
            result['group_id'] = self.group_id
        if self.unsupported_methods:
            result['unsupported_methods'] = self.unsupported_methods
        if self.unsupported_notifications:
            result['unsupported_notifications'] = self.unsupported_notifications
        if self.unsupported_attributes:
            result['unsupported_attributes'] = self.unsupported_attributes
        return result

    def _get_attributes(self, _attributes=None):
        """
        attributes:
            - None = body empty and means request all attributes
            - Empty array means request all attributes
            - Array of attributes (string) and means request attributes in the
              list

        TODO: (Waiting for spec. decision) add test on attribute devices
            - case physical sensor not responding or value not ready add error
            with specific error code and with value = suspicious/stale/cached
        """
        result = {}
        dev_attr = {attr.name: attr for attr in self.__attributes}
        if _attributes:
            # Process attributes filter
            for attr in _attributes:
                if attr in dev_attr.keys():
                    result.update({dev_attr[attr].name: dev_attr[attr].value})
                else:
                    logger.debug(f"Attribute {attr} not found")
        else:
            # Process all attributes
            for attr in dev_attr.values():
                result.update({attr.name: attr.value})
        return result

    def send_notification(self, notification: str, body: dict = {}):
        """queue an notification, this is just a method helper"""
        if self.engine:
            self.engine.send_notification(self, notification, body)
