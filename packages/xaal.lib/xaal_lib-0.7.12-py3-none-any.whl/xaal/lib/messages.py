#
#  Copyright 2014, Jérôme Colin, Jérôme Kerdreux, Philippe Tanguy,
# Telecom Bretagne.
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

import datetime
import logging
import pprint
import struct
import typing
from enum import Enum
from typing import Any, Optional

import pysodium
from tabulate import tabulate

from . import cbor, tools
from .bindings import UUID
from .config import config
from .exceptions import MessageError, MessageParserError

if typing.TYPE_CHECKING:
    from .devices import Device


logger = logging.getLogger(__name__)

ALIVE_ADDR = UUID("00000000-0000-0000-0000-000000000000")


class MessageType(Enum):
    NOTIFY = 0
    REQUEST = 1
    REPLY = 2


class MessageAction(Enum):
    ALIVE = 'alive'
    IS_ALIVE = 'is_alive'
    ATTRIBUTES_CHANGE = 'attributes_change'
    GET_ATTRIBUTES = 'get_attributes'
    GET_DESCRIPTION = 'get_description'


class Message(object):
    """Message object used for incomming & outgoint message"""

    __slots__ = ['version', 'timestamp', 'source', 'dev_type', 'msg_type', 'action', 'body', '__targets']

    def __init__(self):
        self.version = config.STACK_VERSION  # message API version
        self.__targets = []  # target property
        self.timestamp: tuple = ()  # message timestamp
        self.source: Optional[UUID] = None  # message source
        self.dev_type: Optional[str] = None  # message dev_type
        self.msg_type: Optional[MessageType] = None  # message type
        self.action: Optional[str] = None  # message action
        self.body = {}  # message body

    @property
    def targets(self) -> list:
        return self.__targets

    @targets.setter
    def targets(self, values: list):
        if not isinstance(values, list):
            raise MessageError("Expected a list for targetsList, got %s" % (type(values),))
        for uid in values:
            if not tools.is_valid_address(uid):
                raise MessageError("Bad target addr: %s" % uid)
        self.__targets = values

    def targets_as_string(self) -> list:
        return [str(k) for k in self.targets]

    def dump(self):
        r = []
        r.append(['version', self.version])
        r.append(['targets', str(self.targets)])
        r.append(['timestamp', str(self.timestamp)])
        r.append(['source', self.source])
        r.append(['dev_type', self.dev_type])
        r.append(['msg_type', MessageType(self.msg_type)])
        r.append(['action', self.action])
        if self.body:
            tmp = ""
            for k, v in self.body.items():
                k = k + ":"
                v = pprint.pformat(v, width=55)
                tmp = tmp + "- %-12s %s\n" % (k, v)
            # tmp = tmp.strip()
            r.append(['body', tmp])
        print(tabulate(r, headers=['Field', 'Value'], tablefmt='psql'))

    def __repr__(self) -> str:
        return f"<xaal.Message {id(self):x} {self.source} {self.dev_type} {self.msg_type} {self.action}>"

    def is_request(self) -> bool:
        if MessageType(self.msg_type) == MessageType.REQUEST:
            return True
        return False

    def is_reply(self) -> bool:
        if MessageType(self.msg_type) == MessageType.REPLY:
            return True
        return False

    def is_notify(self) -> bool:
        if MessageType(self.msg_type) == MessageType.NOTIFY:
            return True
        return False

    def is_alive(self) -> bool:
        if self.is_notify() and self.action == MessageAction.ALIVE.value:
            return True
        return False

    def is_request_isalive(self) -> bool:
        if self.is_request() and self.action == MessageAction.IS_ALIVE.value:
            return True
        return False

    def is_attributes_change(self) -> bool:
        if self.is_notify() and self.action == MessageAction.ATTRIBUTES_CHANGE.value:
            return True
        return False

    def is_get_attribute_reply(self) -> bool:
        if self.is_reply() and self.action == MessageAction.GET_ATTRIBUTES.value:
            return True
        return False

    def is_get_description_reply(self) -> bool:
        if self.is_reply() and self.action == MessageAction.GET_DESCRIPTION.value:
            return True
        return False


class MessageFactory(object):
    """Message Factory:
    - Build xAAL message
    - Apply security layer, Ciphering/De-Ciphering chacha20 poly1305
    - Serialize/Deserialize data in CBOR"""

    def __init__(self, cipher_key):
        # key encode / decode message built from passphrase
        self.cipher_key = cipher_key

    def encode_msg(self, msg: Message) -> bytes:
        """Apply security layer and return encode MSG in CBOR
        :param msg: xAAL msg instance
        :type msg: Message
        :return: return an xAAL msg ciphered and serialized in CBOR
        :rtype: CBOR
        """

        # Format security layer
        result = []
        result.append(msg.version)
        result.append(msg.timestamp[0])
        result.append(msg.timestamp[1])
        # list of UUID in bytes format (no Tag here)
        result.append(cbor.dumps([t.bytes for t in msg.targets]))

        # Format payload & ciphering
        buf = []
        if not msg.source:
            raise MessageError("No source address in message")
        if not msg.msg_type:
            raise MessageError("No msg_type in message")
        buf.append(msg.source.bytes)
        buf.append(msg.dev_type)
        buf.append(msg.msg_type.value)
        buf.append(msg.action)
        if msg.body:
            buf.append(msg.body)
        clear = cbor.dumps(buf)
        # Additionnal Data == cbor serialization of the targets array
        ad = result[3]
        nonce = build_nonce(msg.timestamp)
        payload = pysodium.crypto_aead_chacha20poly1305_ietf_encrypt(clear, ad, nonce, self.cipher_key)

        # Final CBOR serialization
        result.append(payload)
        pkt = cbor.dumps(result)
        return pkt

    def decode_msg(self, data: bytes, filter_func: Any = None) -> Optional[Message]:
        """Decode incoming CBOR data and De-Ciphering
        :param data: data received from the multicast bus
        :type data: cbor
        :filter_func: function to filter incoming messages
        :type filter_func: function
        :return: xAAL msg
        :rtype: Message
        """
        # Decode cbor incoming data
        try:
            data_rx = cbor.loads(data)
        except Exception:
            raise MessageParserError("Unable to parse CBOR data")

        # Instanciate Message, parse the security layer
        msg = Message()
        try:
            msg.version = data_rx[0]
            msg_time = data_rx[1]
            targets = cbor.loads(data_rx[3])
            msg.targets = [UUID(bytes=t) for t in targets]
            msg.timestamp = (data_rx[1], data_rx[2])
        except IndexError:
            raise MessageParserError("Bad Message, wrong fields")

        # filter some messages
        if filter_func is not None:
            if not filter_func(msg):
                return None  # filter out the message

        # Replay attack, window fixed to CIPHER_WINDOW in seconds
        now = build_timestamp()[0]  # test done only on seconds ...
        if msg_time < (now - config.cipher_window):
            raise MessageParserError("Potential replay attack, message too old: %d sec" % round(now - msg_time))

        if msg_time > (now + config.cipher_window):
            raise MessageParserError("Potential replay attack, message too young: %d sec" % round(now - msg_time))

        # Payload De-Ciphering
        try:
            ciph = data_rx[4]
        except IndexError:
            raise MessageParserError("Bad Message, no payload found!")

        # chacha20 deciphering
        ad = data_rx[3]
        nonce = build_nonce(msg.timestamp)
        try:
            clear = pysodium.crypto_aead_chacha20poly1305_ietf_decrypt(ciph, ad, nonce, self.cipher_key)
        except Exception:
            raise MessageParserError("Unable to decrypt msg")

        # Decode application layer (payload)
        try:
            payload = cbor.loads(clear)
        except Exception:
            raise MessageParserError("Unable to parse CBOR data in payload after decrypt")
        try:
            msg.source = UUID(bytes=payload[0])
            msg.dev_type = payload[1]
            msg.msg_type = payload[2]
            msg.action = payload[3]
        except IndexError:
            raise MessageParserError("Unable to parse payload headers")
        if len(payload) == 5:
            msg.body = payload[4]

        # Sanity check incomming message
        if not tools.is_valid_address(msg.source):
            raise MessageParserError("Wrong message source [%s]" % msg.source)
        if not tools.is_valid_dev_type(msg.dev_type):
            raise MessageParserError("Wrong message dev_type [%s]" % msg.dev_type)
        return msg

    #####################################################
    # MSG builder
    #####################################################
    def build_msg(
        self,
        dev: Optional['Device'] = None,
        targets: list = [],
        msg_type: Optional[MessageType] = None,
        action: Optional[str] = None,
        body: Optional[dict] = None,
    ):
        """the build method takes in parameters :
        -A device
        -The list of targets of the message
        -The type of the message
        -The action of the message
        -A body if it's necessary (None if not)
        it will return a message encoded in CBOR and ciphered.
        """
        message = Message()
        if dev:
            message.source = dev.address
            message.dev_type = dev.dev_type

        message.targets = targets
        message.timestamp = build_timestamp()

        if msg_type:
            message.msg_type = msg_type
        if action:
            message.action = action
        if body is not None and body != {}:
            message.body = body

        data = self.encode_msg(message)
        return data

    def build_alive_for(self, dev: 'Device', timeout: int = 0) -> bytes:
        """Build Alive message for a given device
        timeout = 0 is the minimum value
        """
        body = {}
        body['timeout'] = timeout
        message = self.build_msg(
            dev=dev, targets=[], msg_type=MessageType.NOTIFY, action=MessageAction.ALIVE.value, body=body
        )
        return message

    def build_error_msg(self, dev: 'Device', errcode: int, description: Optional[str] = None):
        """Build a Error message"""
        message = Message()
        body = {}
        body['code'] = errcode
        if description:
            body['description'] = description
        message = self.build_msg(dev, [], MessageType.NOTIFY, 'error', body)
        return message


def build_nonce(data: tuple) -> bytes:
    """Big-Endian, time in seconds and time in microseconds"""
    nonce = struct.pack(">QL", data[0], data[1])
    return nonce


def build_timestamp() -> tuple:
    """Return array [seconds since epoch, microseconds since last seconds] Time = UTC+0000"""
    utc = datetime.timezone.utc
    epoch = datetime.datetime.fromtimestamp(0, utc)
    timestamp = datetime.datetime.now(utc) - epoch
    return (int(timestamp.total_seconds()), int(timestamp.microseconds))


## This stuff below is for Py2/Py3 compatibility. In the current state of xAAL, we only use
# Py3. This code is here for archive purpose and could be removed in the future.

# for better performance, I choose to use this trick to fix the change in size for Py3.
# only test once.
# if sys.version_info.major == 2:
#    _packtimestamp = lambda t1, t2: (long(t1), int(t2)) # pyright: ignore
# else:
#    _packtimestamp = lambda t1, t2: (int(t1), int(t2))
