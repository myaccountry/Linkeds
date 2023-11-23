from SERVER.request_handler import RequestHandler

SERVER_IP = '127.0.0.1'
SERVER_PORT = 25565

METHODS = {}
for key, value in RequestHandler.__dict__.items():
    if key[:2] != '__' and key[-2:] != '__':
        METHODS[f"<{key.upper().replace('_', '-')}>"] = key
