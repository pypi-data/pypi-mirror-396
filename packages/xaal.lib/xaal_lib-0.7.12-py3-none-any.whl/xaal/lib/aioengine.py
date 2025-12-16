import asyncio
import logging
import signal
import sys
import time
import typing
from enum import Enum
from pprint import pprint
from typing import Any, Optional
from uuid import UUID

import aioconsole
from tabulate import tabulate

from .config import config
from . import core
from .aionetwork import AsyncNetworkConnector
from .exceptions import CallbackError, XAALError
from .messages import MessageParserError

if typing.TYPE_CHECKING:
    from .devices import Device
    from .messages import Message

logger = logging.getLogger(__name__)


#####################################################
# Hooks
#####################################################
class HookType(Enum):
    start = 0
    stop = 1


class Hook(object):
    __slots__ = ['type', 'func', 'args', 'kwargs']

    def __init__(self, type_: HookType, func: core.FuncT, *args, **kwargs):
        # func has to be a callable, but it can be a coroutine or a function
        self.type = type_
        self.func = func
        self.args = args
        self.kwargs = kwargs


class AsyncEngine(core.EngineMixin):
    __slots__ = [
        '__txFifo',
        '_loop',
        '_tasks',
        '_hooks',
        '_watchdog_task',
        '_kill_counter',
        'running_event',
        'watchdog_event',
        'started_event',
    ]

    def __init__(
        self, address: str = config.address, port: int = config.port, hops: int = config.hops, key: bytes = config.key
    ):
        core.EngineMixin.__init__(self, address, port, hops, key)

        self.__txFifo = asyncio.Queue()  # tx msg fifo
        self._loop = None  # event loop
        self._hooks = []  # hooks
        self._tasks = []  # tasks
        self._watchdog_task = None  # watchdog task
        self._kill_counter = 0  # watchdog counter

        self.started_event = asyncio.Event()  # engine started event
        self.running_event = asyncio.Event()  # engine running event
        self.watchdog_event = asyncio.Event()  # watchdog event

        signal.signal(signal.SIGTERM, self.sigkill_handler)
        signal.signal(signal.SIGINT, self.sigkill_handler)

        # message receive workflow
        self.subscribe(self.handle_request)
        # start network
        self.network = AsyncNetworkConnector(address, port, hops)

    #####################################################
    # Hooks
    #####################################################
    def on_start(self, func: core.FuncT, *args, **kwargs):
        hook = Hook(HookType.start, func, *args, **kwargs)
        self._hooks.append(hook)

    def on_stop(self, func: core.FuncT, *args, **kwargs):
        hook = Hook(HookType.stop, func, *args, **kwargs)
        self._hooks.append(hook)

    async def run_hooks(self, hook_type: HookType):
        hooks = list(filter(lambda hook: hook.type == hook_type, self._hooks))
        if len(hooks) != 0:
            logger.debug(f"Launching {hook_type} hooks")
            for h in hooks:
                await run_func(h.func, *h.args, **h.kwargs)

    #####################################################
    # timers
    #####################################################
    async def process_timers(self):
        """Process all timers to find out which ones should be run"""
        expire_list = []
        now = time.time()
        for t in self.timers:
            if t.deadline < now:
                try:
                    await run_func(t.func)
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

    #####################################################
    # msg send / receive
    #####################################################
    def queue_msg(self, msg: bytes):
        """queue a message"""
        self.__txFifo.put_nowait(msg)

    def send_msg(self, msg: bytes):
        """Send an encoded message to the bus, use queue_msg instead"""
        self.network.send(msg)

    async def receive_msg(self) -> Optional['Message']:
        """return new received message or None"""
        data = await self.network.get_data()
        if data:
            try:
                msg = self.msg_factory.decode_msg(data, self.msg_filter)
            except MessageParserError as e:
                logger.warning(e)
                msg = None
            return msg
        return None

    async def process_rx_msg(self):
        """process incomming messages"""
        msg = await self.receive_msg()
        if msg:
            for func in self.subscribers:
                await run_func(func, msg)
            self.process_attributes_change()

    def handle_request(self, msg: 'Message'):
        """Filter msg for devices according default xAAL API then process the
        request for each targets identied in the engine
        """
        if not msg.is_request():
            return

        targets = core.filter_msg_for_devices(msg, self.devices)
        for target in targets:
            if msg.is_request_isalive():
                self.send_alive(target)
            else:
                self.new_task(self.handle_action_request(msg, target))

    async def handle_action_request(self, msg: 'Message', target: 'Device'):
        if msg.action is None:
            return  # should not happen, but pyright need this check

        try:
            result = await run_action(msg, target)
            if result is not None and type(result) is dict:
                self.send_reply(dev=target, targets=[msg.source], action=msg.action, body=result)
        except CallbackError as e:
            self.send_error(target, e.code, e.description)
        except XAALError as e:
            logger.error(e)

    #####################################################
    # Asyncio loop & Tasks
    #####################################################
    def get_loop(self) -> asyncio.AbstractEventLoop:
        if self._loop is None:
            logger.debug("New event loop")
            self._loop = asyncio.get_event_loop()
        return self._loop

    def new_task(self, coro: Any, name: Optional[str] = None) -> asyncio.Task:
        # we maintain a task list, to be able to stop/start the engine
        # on demand. needed by HASS
        task = self.get_loop().create_task(coro, name=name)
        self._tasks.append(task)
        task.add_done_callback(self.task_callback)
        return task

    def task_callback(self, task: asyncio.Task):
        # called when a task ended
        self._tasks.remove(task)

    def all_tasks(self) -> typing.List[asyncio.Task]:
        return self._tasks

    async def boot_task(self):
        self.watchdog_event.clear()
        # queue the alive before anything
        for dev in self.devices:
            self.send_alive(dev)
        await self.network.connect()
        self.running_event.set()
        await self.run_hooks(HookType.start)

    async def receive_task(self):
        await self.running_event.wait()
        while self.is_running():
            await self.process_rx_msg()

    async def send_task(self):
        await self.running_event.wait()
        while self.is_running():
            temp = await self.__txFifo.get()
            self.send_msg(temp)

    async def timer_task(self):
        await self.running_event.wait()
        self.setup_alives_timer()
        while self.is_running():
            await asyncio.sleep(0.2)
            await self.process_timers()
            self.process_attributes_change()

    async def watchdog_task(self):
        await self.watchdog_event.wait()
        await self.stop()
        logger.info("Exit")

    #####################################################
    # start / stop / shutdown
    #####################################################
    def is_running(self) -> bool:
        return self.running_event.is_set()

    def start(self):
        if self.is_running():
            logger.warning("Engine already started")
            return
        self.started_event.set()
        self.new_task(self.boot_task(), name='Boot')
        self.new_task(self.receive_task(), name='RecvQ')
        self.new_task(self.send_task(), name='SendQ')
        self.new_task(self.timer_task(), name='Timers')
        if config.remote_console:
            self.new_task(console(locals()), name='Console')

    def setup_alives_timer(self):
        # needed on stop-start sequence
        if self.process_alives in [t.func for t in self.timers]:
            return
        # process alives every 10 seconds
        self.add_timer(self.process_alives, 10)

    async def stop(self):  # pyright: ignore
        logger.info("Stopping engine")
        await self.run_hooks(HookType.stop)
        self.running_event.clear()
        self.started_event.clear()
        # cancel all tasks
        for task in self.all_tasks():
            if task != self._watchdog_task and not task.cancelled():
                task.cancel()

    def sigkill_handler(self, signal, frame):
        print("", end="\r")  # remove the uggly ^C
        if not self.is_running():
            logger.warning("Engine already stopped")
            self._kill_counter = 1
        self._kill_counter += 1
        self.shutdown()
        if self._kill_counter > 1:
            logger.warning("Force quit")
            sys.exit(-1)
        else:
            logger.warning("Kill requested")

    def shutdown(self):
        self.watchdog_event.set()

    def run(self):
        if not self.started_event.is_set():
            self.start()
        if self._watchdog_task is None:
            # start the watchdog task
            self._watchdog_task = self.new_task(self.watchdog_task(), name="Watchdog task")
            self.get_loop().run_until_complete(self._watchdog_task)
        else:
            logger.warning("Engine already running")

    #####################################################
    # Debugging tools
    #####################################################
    def dump_timers(self):
        headers = ['Func', 'Period', 'Counter', 'Deadline']
        rows = []
        now = time.time()
        for t in self.timers:
            remain = round(t.deadline - now, 1)
            rows.append([str(t.func), t.period, t.counter, remain])
        print("= Timers")
        print(tabulate(rows, headers=headers, tablefmt='fancy_grid'))

    def dump_tasks(self):
        headers = ['Name', 'Coro', 'Loop ID']
        rows = []
        for t in self.all_tasks():
            rows.append([t.get_name(), str(t.get_coro()), id(t.get_loop())])
        print("= Tasks")
        print(tabulate(rows, headers=headers, tablefmt='fancy_grid'))

    def dump_devices(self):
        headers = ['addr', 'dev_type', 'info']
        rows = []
        for d in self.devices:
            rows.append([d.address, d.dev_type, d.info])
        print("= Devices")
        print(tabulate(rows, headers=headers, tablefmt='fancy_grid'))

    def dump_hooks(self):
        headers = ['Type', 'Hook']
        rows = []
        for h in self._hooks:
            rows.append([h.type, str(h.func)])
        print("= Hooks")
        print(tabulate(rows, headers=headers, tablefmt='fancy_grid'))

    def dump(self):
        self.dump_devices()
        self.dump_tasks()
        self.dump_timers()
        self.dump_hooks()

    def get_device(self, uuid: UUID) -> Optional['Device']:
        # TODO:Check if this method is usefull
        for dev in self.devices:
            if dev.address == uuid:
                return dev
        return None


#####################################################
# Utilities functions
#####################################################
async def run_func(func, *args, **kwargs):
    """run a function or a coroutine function"""
    if asyncio.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    else:
        return func(*args, **kwargs)


async def run_action(msg: 'Message', device: 'Device'):
    """
    Extract an action & launch it
    Return:
        - action result
        - None if no result

    Notes:
        - If an exception raised, it's logged, and raise an XAALError.
        - Same API as legacy Engine, but accept coroutine functions
    """
    method, params = core.search_action(msg, device)
    result = None
    try:
        if asyncio.iscoroutinefunction(method):
            result = await method(**params)
        else:
            result = method(**params)
    except Exception as e:
        logger.error(e)
        raise XAALError("Error in method:%s params:%s" % (msg.action, params))
    return result


#####################################################
# Debugging console
#####################################################
async def console(locals=locals(), port: Optional[int] = None):
    """launch a console to enable remote engine inspection"""
    if port is None:
        # let's find a free port if not specified
        def find_free_port():
            import socketserver

            with socketserver.TCPServer(('localhost', 0), None) as s:  # pyright: ignore pyright reject the None here
                return s.server_address[1]

        port = find_free_port()

    logger.debug(f"starting debug console on port {port}")
    sys.ps1 = "[xAAL] >>> "
    banner = "=" * 78 + "\nxAAL remote console\n" + "=" * 78
    locals.update({'pprint': pprint})

    def factory(streams):
        return aioconsole.AsynchronousConsole(locals=locals, streams=streams)

    # start the console
    try:
        # debian with ipv6 disabled still state that localhost is ::1, which broke aioconsole
        await aioconsole.start_interactive_server(
            host="127.0.0.1", port=port, factory=factory, banner=banner
        )  # pyright: ignore
    except OSError:
        logger.warning("Unable to run console")
