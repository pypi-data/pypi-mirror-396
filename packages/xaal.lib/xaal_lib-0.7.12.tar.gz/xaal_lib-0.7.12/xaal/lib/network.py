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
import select
import socket
import struct
import time
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class NetworkState(Enum):
    disconnected = 0
    connected = 1


class NetworkConnector(object):
    UDP_MAX_SIZE = 65507

    def __init__(self, addr: str, port: int, hops: int, bind_addr="0.0.0.0"):
        self.addr = addr
        self.port = port
        self.hops = hops
        self.bind_addr = bind_addr
        self.state = NetworkState.disconnected

    def connect(self):
        try:
            self.__connect()
        except Exception as e:
            self.network_error(e)

    def __connect(self):
        logger.info("Connecting to %s:%s" % (self.addr, self.port))

        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        # #formac os ???
        # self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__sock.bind((self.bind_addr, self.port))
        mreq = struct.pack("=4s4s", socket.inet_aton(self.addr), socket.inet_aton(self.bind_addr))
        self.__sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.__sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.hops)
        self.state = NetworkState.connected

    def disconnect(self):
        logger.info("Disconnecting from the bus")
        self.state = NetworkState.disconnected
        self.__sock.close()

    def is_connected(self):
        return self.state == NetworkState.connected

    def receive(self) -> bytes:
        packt = self.__sock.recv(self.UDP_MAX_SIZE)
        return packt

    def __get_data(self) -> Optional[bytes]:
        r = select.select([self.__sock,], [], [], 0.02)
        if r[0]:
            return self.receive()
        return None

    def get_data(self) -> Optional[bytes]:
        if not self.is_connected():
            self.connect()
        try:
            return self.__get_data()
        except Exception as e:
            self.network_error(e)

    def send(self, data: bytes):
        if not self.is_connected():
            self.connect()
        try:
            self.__sock.sendto(data, (self.addr, self.port))
        except Exception as e:
            self.network_error(e)

    def network_error(self, ex: Exception):
        self.disconnect()
        logger.info("Network error, reconnect..%s" % ex.__str__())
        time.sleep(5)
