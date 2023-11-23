import logging
import asyncio
from asyncio import BaseTransport, Protocol
from threading import Thread
from request_handler import RequestHandler
from LOGS.logger import CustomFormatter, init_logger
from CONFIG.server_config import *

CONNECTIONS = {}


class ServerProtocol(Protocol):
    """
    Server Protocol Class Object to listen for connection
    and start work with ConnectionHandler after getting request
    """

    def __init__(self):
        self._transport = None
        self.addr = None
        self._connection = None

    def connection_made(self, transport: BaseTransport) -> None:
        """
        Method create link for transport and create ConnectionsHandler
        to process data
        """
        self._transport = transport
        self.addr = self.transport.get_extra_info("peername")
        self._connection = ConnectionsHandler(self._transport)

    def data_received(self, data: bytes) -> None:
        """
        Sending data to ConnectionHandler
        """
        self._connection.data_received(data=data)

    def connection_lost(self, exc: Exception | None) -> None:
        self._connection.connection_lost(exc=exc)


class ConnectionsHandler(Thread, ServerProtocol):
    """
    ConnectionHandler use threads to process with
    client requests, all received data sends to RequestHandler
    """
    def __init__(self, transport: BaseTransport):
        """
        Init some specified data and creating RequestHandler class object
        """
        addr = transport.get_extra_info('peername')
        Thread.__init__(self, name=addr)

        self._addr = addr
        self._transport = transport
        self.request_handler = RequestHandler(self._transport)

    def data_received(self, data: bytes) -> None:
        """
        Received data sends to RequestHandler to process
        """
        ...

    def connection_lost(self, exc: Exception | None) -> None:
        """
        Connection lost
        """
        ...


async def main():
    """
    Get a reference to an event loop
    """
    loop = asyncio.get_running_loop()

    logging.info('<SERVER-RISE>')
    server = await loop.create_server(lambda: ServerProtocol(), '192.168.1.61', 25565)

    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    logging.debug(msg=init_logger('server'))
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('<SERVER-SET>')
