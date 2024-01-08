import sys
import pathlib

import DATABASE.database

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
from DATABASE.database import Database

CONNECTIONS = {}
HANDLERS = []


class ServerProtocol(Protocol):
    global CONNECTIONS
    global HANDLERS
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
        HANDLERS.append(self._connection)
        logging.debug(msg=HANDLERS)
        for handler in HANDLERS:
            handler.request_handler.CONNECTIONS = CONNECTIONS

    def data_received(self, data: bytes) -> None:
        """
        Sending data to ConnectionHandler
        """
        self._connection.data_received(data=data)

    def connection_lost(self, exc: Exception | None) -> None:
        self._connection.connection_lost(exc=exc)


class ConnectionsHandler(Thread, ServerProtocol):
    global CONNECTIONS
    global HANDLERS
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
        self.request_handler = RequestHandler(self._transport, self)

        global CONNECTIONS
        global HANDLERS
        CONNECTIONS[self._addr] = {'addr': self._addr, 'transport': self._transport}
        logging.debug(msg=CONNECTIONS)

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

    @staticmethod
    def send_request_to(data, addr) -> None:
        transport = CONNECTIONS.get(addr)
        transport.write(pickle.dumps(data) + b"<END>")

    def close_connection(self) -> None:
        self._transport.close()

    def connection_lost(self, exc: Exception | None) -> None:
        logging.info(msg=f'Connection with {self._addr[0]}:{self._addr[1]} closed')
        self.request_handler.database.connect()
        connection = self.request_handler.database.select(
            table_name='connection', criterion='ip', id=f"{self._addr[0]}:{self._addr[1]}")
        if connection != tuple([]):
            if exc is not None:
                logging.debug(msg=f'Error from Client App: {str(exc)}')
            logging.debug(msg=f"Connection: {connection[0].get('ip')} | ID: {connection[0].get('id')}")
            user_data = pickle.loads(self.request_handler.database.select(
                table_name='connection', criterion='ip', id=f"{self._addr[0]}:{self._addr[1]}")[0].get('user_data'))
            self.request_handler.offline({'user_data': user_data})
        del CONNECTIONS[self._addr]
        del HANDLERS[HANDLERS.index(self)]
        del self


async def main():
    global CONNECTIONS
    global HANDLERS
    """
    Get a reference to an event loop
    """
    loop = asyncio.get_running_loop()

    logging.info('<SERVER-RISE>')
    server = await loop.create_server(lambda: ServerProtocol(), SERVER_IP, SERVER_PORT)

    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    logging.debug(msg=init_logger('server'))
    try:
        db_check = Database()
    except ConnectionError:
        logging.error(msg='Can\'t connect to Database')
        exit()
    db_check.connect()
    for el in db_check.select(table_name='connection', subject='id'):
        db_check.delete(table_name='connection', id=el.get('id'))
    logging.debug(db_check.update(subject='online', subject_value='False'))
    del db_check
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('<SERVER-SET-WITH-KEYBOARD-INTERRUPT>')
    finally:
        logging.info('<SERVER-SET>')
        time.sleep(3)
