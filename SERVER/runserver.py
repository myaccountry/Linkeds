import asyncio
import threading
from asyncio import BaseTransport, Protocol

CONNECTIONS = {}


class ServerProtocol(Protocol):
    """
    Server Protocol Class Object to listen for connection
    and start work with ConnectionHandler after getting request
    """
    addr: object
    transport: BaseTransport

    def connection_made(self, transport: transports.BaseTransport) -> None:
        self.transport = transport
        self.addr = self.transport.get_extra_info("peername")

    def data_received(self, data: bytes) -> None:
        ...


if __name__ == '__main__':
    ...
