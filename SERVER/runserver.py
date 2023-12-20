import sys
import pathlib

path = '\\'.join(str(pathlib.Path().resolve()).split('\\')[:-1])
sys.path.insert(0, f'{path}')

import logging
import asyncio
import time
import pickle
from asyncio import BaseTransport, Protocol
from threading import Thread
from request_handler import RequestHandler
from LOGS.logger import init_logger
from CONFIG.server_config import SERVER_IP, SERVER_PORT

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
        self.addr = self._transport.get_extra_info("peername")
        logging.info(f'Connection from {self.addr[0]}:{self.addr[1]}')
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

        CONNECTIONS[self._addr] = {'addr': self._addr, 'transport': self._transport, 'in_app': False}

        self.usable_data = b""
        self.current_data = b""

    def data_received(self, data: bytes) -> None:
        """
        Received data sends to RequestHandler to process
        """
        self.current_data += data

        if b"<END>" in self.current_data:
            self.usable_data = self.current_data.replace(b'<END>', b'')
            self.current_data = b''
            self.usable_data = pickle.loads(self.usable_data)
        else:
            return

        logging.info(msg=f'Received request {self.usable_data.get("method")} from {self._addr[0]}:{self._addr[1]}')
        try:
            status = self.request_handler.call_method(self.usable_data)
        except Exception as error:
            status = {'method': '<CLOSE-CONNECTION>', 'data': 'None'}
            logging.error(msg=error)
        if status.get('method') == '<CLOSE-CONNECTION>':
            self.close_connection()
        if status.get('method') != '<COMPLETE>':
            self.send_request(status)
        logging.info(msg=f'Reguest {self.usable_data.get("method")} status')
        logging.info(msg=f'For {self._addr[0]}:{self._addr[1]}: {status.get("method")}')

    def send_request(self, data) -> None:
        self._transport.write(pickle.dumps(data) + b"<END>")

    def close_connection(self) -> None:
        self._transport.close()

    def connection_lost(self, exc: Exception | None) -> None:
        logging.info(msg=f'Connection with {self._addr[0]}:{self._addr[1]} closed')
        if exc is not None:
            logging.info(msg=f'Error from Client App: {str(exc)}')
        del CONNECTIONS[self._addr]
        del self


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
        logging.info('<SERVER-SET-WITH-KEYBOARD-INTERRUPT>')
    finally:
        logging.info('<SERVER-SET>')
        time.sleep(3)
