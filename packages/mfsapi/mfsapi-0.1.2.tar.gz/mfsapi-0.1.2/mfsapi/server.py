import socket
import threading
from .config import HOST, PORT, BUFFER_SIZE, BACKLOG


class ClientConnection:
    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self.lock = threading.Lock()

    def send(self, data: bytes):
        with self.lock:
            try:
                self.sock.sendall(data)
            except Exception:
                pass

    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass


class MainServer:
    def __init__(self, host=None, port=None, backlog=None, buffer_size=None):
        self.host = host or HOST
        self.port = port or PORT
        self.backlog = backlog or BACKLOG
        self.buffer_size = buffer_size or BUFFER_SIZE

        self.on_receive = None
        self._running = False
        self._sock = None

    def start(self):
        self._running = True
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self.host, self.port))
        self._sock.listen(self.backlog)

        while self._running:
            client_sock, addr = self._sock.accept()
            conn = ClientConnection(client_sock, addr)
            threading.Thread(
                target=self._client_loop,
                args=(conn,),
                daemon=True
            ).start()

    def stop(self):
        self._running = False
        try:
            self._sock.close()
        except Exception:
            pass

    def _client_loop(self, conn: ClientConnection):
        try:
            while self._running:
                data = conn.sock.recv(self.buffer_size)
                if not data:
                    break

                if self.on_receive:
                    response = self.on_receive(conn, data)
                    if response:
                        conn.send(response)
        finally:
            conn.close()