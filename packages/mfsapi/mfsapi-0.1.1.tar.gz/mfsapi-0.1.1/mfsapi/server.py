import socket
import threading
import traceback
from .config import HOST, PORT, BUFFER_SIZE, BACKLOG

class ClientConnection:
    """Wrapper for a connected client socket."""

    def __init__(self, sock, addr):
        self._sock = sock
        self.addr = addr
        self.lock = threading.Lock()

    def send(self, data: bytes):
        """Send raw bytes to the client. Thread-safe."""
        with self.lock:
            try:
                self._sock.sendall(data)
            except Exception:
                pass

    def fileno(self):
        return self._sock.fileno()

    def close(self):
        try:
            self._sock.close()
        except Exception:
            pass


class MainServer:
    """Fully free TCP server skeleton."""

    def __init__(self, host: str = None, port: int = None, backlog: int = None, buffer_size: int = None):
        self.host = host or HOST
        self.port = port or PORT
        self.backlog = backlog or BACKLOG
        self.buffer_size = buffer_size or BUFFER_SIZE

        self.on_connect = None
        self.on_receive = None
        self.on_disconnect = None
        self.on_error = None

        self._sock = None
        self._running = threading.Event()
        self._threads = []

    def start(self, blocking: bool = True):
        if self._running.is_set():
            raise RuntimeError("Server already running")

        self._running.set()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self.host, self.port))
        self._sock.listen(self.backlog)
        self._sock.setblocking(True)

        self._accept_thread = threading.Thread(target=self._accept_loop, name="ssapi-accept")
        self._accept_thread.daemon = True
        self._accept_thread.start()

        if blocking:
            try:
                while self._running.is_set():
                    self._accept_thread.join(timeout=1)
            except KeyboardInterrupt:
                self.stop()

    def stop(self):
        if not self._running.is_set():
            return
        self._running.clear()
        try:
            if self._sock:
                try:
                    self._sock.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                self._sock.close()
        except Exception:
            pass

        for t in list(self._threads):
            if t.is_alive():
                t.join(timeout=2)

    def _accept_loop(self):
        try:
            while self._running.is_set():
                try:
                    client_sock, addr = self._sock.accept()
                except OSError:
                    break

                client_sock.setblocking(True)
                conn = ClientConnection(client_sock, addr)

                t = threading.Thread(target=self._client_loop, args=(conn,), name=f"ssapi-client-{addr}")
                t.daemon = True
                t.start()
                self._threads.append(t)
        except Exception:
            traceback.print_exc()

    def _client_loop(self, conn: ClientConnection):
        try:
            if self.on_connect:
                try:
                    self.on_connect(conn)
                except Exception as exc:
                    if self.on_error:
                        self.on_error(conn, exc)

            sock = conn._sock
            while self._running.is_set():
                try:
                    data = sock.recv(self.buffer_size)
                except Exception as exc:
                    if self.on_error:
                        self.on_error(conn, exc)
                    break

                if not data:
                    break

                if self.on_receive:
                    try:
                        result = self.on_receive(conn, data)
                        if isinstance(result, (bytes, bytearray)) and result:
                            conn.send(result)
                    except Exception as exc:
                        if self.on_error:
                            self.on_error(conn, exc)
                        continue

            try:
                if self.on_disconnect:
                    self.on_disconnect(conn)
            except Exception as exc:
                if self.on_error:
                    self.on_error(conn, exc)
        finally:
            try:
                conn.close()
            except Exception:
                pass