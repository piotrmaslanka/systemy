from socket import socket, AF_INET, AF_INET6, SOCK_STREAM, SOCK_DGRAM
from yos.io import NetworkSocket

from ydrp import globals

class NetworkSocketHandling(NetworkSocket):
    
    def __init__(self, socket, is_client, is_connected):
        self.socket = socket
        self.is_client = is_client
        self.is_connected = is_connected
        self.is_failed = False
        self.is_closed = False
        self.writebuf = bytearray()
        self.readbuf = bytearray()
    
    @staticmethod
    def client(socktype, address):
        if socktype in (NetworkSocket.SOCK_TCP, NetworkSocket.SOCK_UDP, NetworkSocket.SOCK_TCPv6, NetworkSocket.SOCK_UDPv6):
            sock = socket(AF_INET if socktype in (NetworkSocket.SOCK_TCP, NetworkSocket.SOCK_UDP) else AF_INET6,
                          SOCK_STREAM if socktype in (NetworkSocket.SOCK_TCP, NetworkSocket.SOCK_TCPv6) else SOCK_DGRAM)
            sock.setblocking(False)
            try:
                sock.connect(address)
            except BlockingIOError:
                pass
        else:
            raise ValueError('Invalid socket type')
    
        return NetworkSocketHandling(sock, True, False)   
    
    def handleRead(self):
        """Called by yNEP if there's data for this socket"""
        try:
            data = self.socket.recv(1024)
        except OSError:
            data.is_failed = True
            return
    
        if len(data) == 0:
            self.is_closed = True
        else:
            self.readbuf.extend(data)
    
    def read(self, length=None):
        try:
            if not self.is_client:
                return self.socket.accept()
            else:
                data = self.readbuf[:length]
                del self.readbuf[:length]
                return data
        except OSError:
            self.is_failed = True

    def register(self, on_readable, on_exception, on_connected, on_closed, on_failure):
       globals.yNEP.addSock(self, on_connected, on_readable, on_closed, on_failure, on_exception)
       
    def write(self, data):
        if not self.is_client:
            raise ValueError('Server socket does not support writes!')
        
        # Attempt speculative execution
        self.writebuf.extend(data)
        try:
            del self.writebuf[:self.socket.send(self.writebuf)]
        except BlockingIOError:
            pass

    def close(self):
        try:
            self.socket.close()
        except OSError:
            self.is_failed = True
            
    def fileno(self):
        return self.socket.fileno()
            
import yos.io
yos.io.NetworkSocket = NetworkSocketHandling