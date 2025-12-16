import asyncio
import logging
import socket
import struct

logger = logging.getLogger(__name__)


class AsyncNetworkConnector(object):
    def __init__(self, addr: str, port: int, hops: int, bind_addr="0.0.0.0"):
        self.addr = addr
        self.port = port
        self.hops = hops
        self.bind_addr = bind_addr
        self._rx_queue = asyncio.Queue()

    async def connect(self):
        loop = asyncio.get_running_loop()
        on_con_lost = loop.create_future()
        self.transport, self.protocol = await loop.create_datagram_endpoint(
            lambda: XAALServerProtocol(on_con_lost, self.receive), sock=self.new_sock()
        )
        # In some conditions (containers), transport is connected but IGMP is delayed (up to 10ms)
        # so we need to wait for IGMP to be really sent.
        await asyncio.sleep(0.05)

    def new_sock(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        try:
            # Linux + MacOS + BSD
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except Exception:
            # Windows
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.bind_addr, self.port))
        mreq = struct.pack("=4s4s", socket.inet_aton(self.addr), socket.inet_aton(self.bind_addr))
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 10)
        sock.setblocking(False)
        return sock

    def send(self, data: bytes):
        self.protocol.datagram_send(data, self.addr, self.port)

    def receive(self, data: bytes):
        self._rx_queue.put_nowait(data)

    async def get_data(self) -> bytes:
        return await self._rx_queue.get()


class XAALServerProtocol(asyncio.Protocol):
    def __init__(self, on_con_lost, on_dtg_recv):
        self.on_con_lost = on_con_lost
        self.on_dtg_recv = on_dtg_recv

    def connection_made(self, transport):
        logger.info("xAAL network connected")
        self.transport = transport

    def error_received(self, exc):
        print("Error received:", exc)
        logger.warning(f"Error received: {exc}")

    def connection_lost(self, exc):
        logger.info(f"Connexion closed: {exc}")
        self.on_con_lost.set_result(True)

    def datagram_send(self, data, ip, port):
        self.transport.sendto(data, (ip, port))

    def datagram_received(self, data, addr):
        # print(f"pkt from {addr}")
        self.on_dtg_recv(data)
