from typing import Generator, TYPE_CHECKING
from socket import error as __error

if TYPE_CHECKING:
    from socket import socket as __socket


SocketError = __error

class Proxy:

    def __init__(self,
        hostname: str,
            port: int
    ):
        
        self.hostname = hostname
        self.port = port

    def enable(self):
        import socks, socket

        socks.set_default_proxy(
            proxy_type = socks.SOCKS5,
            addr = self.hostname,
            port = self.port
        )

        socket.socket = socks.socksocket

    def disable(self, *_):
        import socks

        socks.set_default_proxy(None)

def socket(
    timeout: int = 10,
    addr: str = None,
    port: int = None
):
    from socket import socket, AF_INET, SOCK_STREAM

    s = socket(AF_INET, SOCK_STREAM)
    
    s.settimeout(timeout)

    if (addr != None) and (port != None):
        s.connect((addr, port))
    
    return s

class conn:

    def __init__(self, conn:'__socket'):
        
        self.conn = conn

    def send(self, data):
        from dill import dumps
        from struct import pack

        data = dumps(data)

        # Pack the length into a 4-byte header (e.g., using '!' for network byte order, 'I' for unsigned int)
        header = pack('!I', len(data))

        # Send the header
        self.conn.sendall(header)

        # Send the actual data
        self.conn.sendall(data)

    def recv(self):
        from dill import loads
        from struct import unpack

        # Unpack the length from the header
        length = unpack('!I', 
            self.conn.recv(4)
        )[0]

        # Receive the actual data based on the unpacked length
        data = self.conn.recv(length).decode('utf-8')

        return loads(data)

class host:

    def __init__(self,
        ip: str = '127.0.0.1',
        port: int = 80
    ):
        self.bindings = (ip, port)
        self.s = socket()
        self.start()
    
    def close(self):
        self.s.close()
        self.started = False

    def start(self):
        try:
            self.s.bind(self.bindings)
            self.s.listen()

            self.started = True
        except:
            self.started = False
            return

    def listen(self) -> Generator[conn]:
        while True:
            yield conn(self.s.accept()[0])

def client(
    ip: str = '127.0.0.1',
    port: int = 80,
    timeout: int = 10
):
    try:
        conn_ = socket(timeout=timeout)
        conn_.connect((ip, port))
        return conn(conn_)
    except:
        return None
