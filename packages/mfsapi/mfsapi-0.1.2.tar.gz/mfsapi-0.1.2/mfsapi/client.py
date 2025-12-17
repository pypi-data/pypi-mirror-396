import socket
from .config import BUFFER_SIZE


class MainClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        self.sock = socket.create_connection((self.host, self.port))

    def send(self, data: bytes):
        self.sock.sendall(data)

    def recv(self, bufsize=BUFFER_SIZE) -> bytes:
        return self.sock.recv(bufsize)

    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass