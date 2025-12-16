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

import collections
import logging
import time
import typing
from enum import Enum
from typing import Optional

from .config import config
from . import core
from .exceptions import CallbackError, MessageParserError, XAALError
from .network import NetworkConnector

if typing.TYPE_CHECKING:
    from .devices import Device
    from .messages import Message


logger = logging.getLogger(__name__)


class EngineState(Enum):
    started = 1
    running = 2
    halted = 3


class Engine(core.EngineMixin):
    __slots__ = ['__last_timer', '__txFifo', 'state', 'network']

    def __init__(
        self, address: str = config.address, port: int = config.port, hops: int = config.hops, key: bytes = config.key
    ):
        core.EngineMixin.__init__(self, address, port, hops, key)

        self.__last_timer = 0  # last timer check
        self.__txFifo = collections.deque()  # tx msg fifo
        # message receive workflow
        self.subscribe(self.handle_request)
        # ready to go
        self.state = EngineState.halted
        # start network
        self.network = NetworkConnector(address, port, hops)

    #####################################################
    # xAAL messages Tx handling
    #####################################################
    # Fifo for msg to send
    def queue_msg(self, msg: bytes):
        """queue an encoded / cyphered message"""
        self.__txFifo.append(msg)

    def send_msg(self, msg: bytes):
        """Send an encoded message to the bus, use queue_msg instead"""
        self.network.send(msg)

    def process_tx_msg(self):
        """Process (send) message in tx queue called from the loop()"""
        cnt = 0
        while self.__txFifo:
            temp = self.__txFifo.popleft()
            self.send_msg(temp)
            # try to limit rate
            cnt = cnt + 1
            if cnt > config.queue_size:
                time.sleep(0.2)
                break

    #####################################################
    # xAAL messages subscribers
    #####################################################
    def receive_msg(self) -> Optional['Message']:
        """return new received message or None"""
        result = None
        data = self.network.get_data()
        if data:
            try:
                msg = self.msg_factory.decode_msg(data, self.msg_filter)
            except MessageParserError as e:
                logger.warning(e)
                msg = None
            result = msg
        return result

    def process_subscribers(self):
        """process incomming messages"""
        msg = self.receive_msg()
        if msg:
            for func in self.subscribers:
                func(msg)
            self.process_attributes_change()

    def handle_request(self, msg: 'Message'):
        """
        Filter msg for devices according default xAAL API then process the
        request for each targets identied in the engine
        """
        if not msg.is_request():
            return

        targets = core.filter_msg_for_devices(msg, self.devices)
        for target in targets:
            if msg.is_request_isalive():
                self.send_alive(target)
            else:
                self.handle_action_request(msg, target)

    def handle_action_request(self, msg: 'Message', target: 'Device'):
        """
        Run method (xAAL exposed method) on device:
            - result is returned if device method gives a response
            - Errors are raised if an error occured:
                * Internal error
                * error returned on the xAAL bus
        """
        if msg.action is None:
            return  # should not happen, but pyright need this check

        try:
            result = run_action(msg, target)
            if result is not None:
                self.send_reply(dev=target, targets=[msg.source], action=msg.action, body=result)
        except CallbackError as e:
            self.send_error(target, e.code, e.description)
        except XAALError as e:
            logger.error(e)

    #####################################################
    # timers
    #####################################################
    def process_timers(self):
        """Process all timers to find out which ones should be run"""
        expire_list = []

        if len(self.timers) != 0:
            now = time.time()
            # little hack to avoid to check timer to often.
            # w/ this enable timer precision is bad, but far enougth
            if (now - self.__last_timer) < 0.4:
                return

            for t in self.timers:
                if t.deadline < now:
                    try:
                        t.func()
                    except CallbackError as e:
                        logger.error(e.description)
                    if t.counter != -1:
                        t.counter -= 1
                        if t.counter == 0:
                            expire_list.append(t)
                    t.deadline = now + t.period
            # delete expired timers
            for t in expire_list:
                self.remove_timer(t)

            self.__last_timer = now

    #####################################################
    # Mainloops & run ..
    #####################################################
    def loop(self):
        """
        Process incomming xAAL msg
        Process timers
        Process attributes change for devices
        Process is_alive for device
        Send msgs from the Tx Buffer
        """
        # Process xAAL msg received, filter msg and process request
        self.process_subscribers()
        # Process timers
        self.process_timers()
        # Process attributes change for devices due to timers
        self.process_attributes_change()
        # Process Alives
        self.process_alives()
        # Process xAAL msgs to send
        self.process_tx_msg()

    def start(self):
        """Start the core engine: send queue alive msg"""
        if self.state in [EngineState.started, EngineState.running]:
            return
        self.network.connect()
        for dev in self.devices:
            self.send_alive(dev)
        self.state = EngineState.started

    def stop(self):
        self.state = EngineState.halted

    def shutdown(self):
        self.stop()

    def run(self):
        self.start()
        self.state = EngineState.running
        while self.state == EngineState.running:
            self.loop()

    def is_running(self) -> bool:
        if self.state == EngineState.running:
            return True
        return False


def run_action(msg: 'Message', device: 'Device') -> Optional[dict]:
    """
    Extract an action & launch it
    Return:
        - action result
        - None if no result

    Note: If an exception raised, it's logged, and raise an XAALError.
    """
    method, params = core.search_action(msg, device)
    result = None
    try:
        result = method(**params)
    except Exception as e:
        logger.error(e)
        raise XAALError("Error in method:%s params:%s" % (msg.action, params))
    # Here result should be None or a dict, and we need to enforce that. This will cause issue
    # in send_reply otherwise.
    if result is not None and not isinstance(result, dict):
        raise XAALError("Method %s should return a dict or None" % msg.action)
    return result
