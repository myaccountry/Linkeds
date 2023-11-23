from CONFIG.server_config import *


class RequestHandler:

    def __init__(self, transport):

        self._transport = transport
        self.addr = transport.get("peername")
