import socket
import threading
from typing import Optional
from .config import BUFFER_SIZE

class MainClient:
    """Lightweight TCP client."""

    def __init__(self, host: str, port: int, timeout: Optional[float] = None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._sock = None
        self._recv_lock = threading.Lock()

    def connect(self):
        if self._sock:
            return
        self._sock = socket.create_connection((self.host, self.port), timeout=self.timeout)

    def send(self, data: bytes):
        if not self._sock:
            raise RuntimeError("Not connected")
        self._sock.sendall(data)

    def recv(self, bufsize: int = BUFFER_SIZE) -> bytes:
        if not self._sock:
            raise RuntimeError("Not connected")
        with self._recv_lock:
            return self._sock.recv(bufsize)

    def send_and_recv(self, data: bytes, bufsize: int = BUFFER_SIZE) -> bytes:
        self.send(data)
        return self.recv(bufsize)

    def close(self):
        if self._sock:
            try:
                self._sock.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None