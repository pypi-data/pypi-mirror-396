from .server import MainServer
from .client import MainClient
from .config import ENCODING, HOST, PORT


class Server:
    def __init__(self, host=HOST, port=PORT):
        self._commands = {}
        self._server = MainServer(host, port)
        self._server.on_receive = self._on_receive

    def command(self, name: str):
        def decorator(func):
            self._commands[name.upper()] = func
            return func
        return decorator

    def _on_receive(self, conn, data: bytes):
        text = data.decode(ENCODING).strip()
        if not text:
            return b"ERR empty request"

        parts = text.split(" ", 1)
        cmd = parts[0].upper()
        payload = parts[1] if len(parts) > 1 else ""

        handler = self._commands.get(cmd)
        if not handler:
            return f"ERR unknown command {cmd}".encode(ENCODING)

        try:
            result = handler(payload)
            return f"OK {result}".encode(ENCODING)
        except Exception as e:
            return f"ERR {e}".encode(ENCODING)

    def run(self):
        self._server.start()


class Client:
    def __init__(self, host=HOST, port=PORT):
        self._client = MainClient(host, port)
        self._client.connect()

    def request(self, text: str) -> str:
        self._client.send(text.encode(ENCODING))
        response = self._client.recv().decode(ENCODING)

        if response.startswith("OK "):
            return response[3:]
        if response.startswith("ERR "):
            raise RuntimeError(response[4:])

        return response

    def close(self):
        self._client.close()