from socket import socket, AF_INET, AF_INET6, SOCK_STREAM, SOCK_DGRAM
from yos.io import NetworkSocket

from ypage.nukleon import S

class NetworkSocketHandling(NetworkSocket):
    
    def __init__(self, socket, is_client: bool, is_connected: bool):
        self.socket = socket
        self.is_client = is_client
        self.is_connected = is_connected    
        self.issued_on_connected = False # makes sense only when server
        self.is_failed = False
        self.is_closed = False
        self.writebuf = bytearray()
        self.close_on_all_write = False
        
        self._fileno = socket.fileno()
    
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
    
    @staticmethod
    def server(socktype, address):
        """This is bugged for UDP servers so far"""
        if socktype in (NetworkSocket.SOCK_TCP, NetworkSocket.SOCK_UDP, NetworkSocket.SOCK_TCPv6, NetworkSocket.SOCK_UDPv6):
            sock = socket(AF_INET if socktype in (NetworkSocket.SOCK_TCP, NetworkSocket.SOCK_UDP) else AF_INET6,
                          SOCK_STREAM if socktype in (NetworkSocket.SOCK_TCP, NetworkSocket.SOCK_TCPv6) else SOCK_DGRAM)
            sock.setblocking(False)
            try:
                sock.bind(address)
                sock.listen(10)
            except IOError:
                ns = NetworkSocketHandling(sock, False, True)
                ns.is_failed = True
                return ns
        else:
            raise ValueError('Invalid socket type')
    
        return NetworkSocketHandling(sock, False, True)   
            
    
    def handleRead(self):
        """Called by yNEP if there's data for this socket.
        Returns readed entry if there is data, None if closed or failed"""
        if self.is_client:
            try:
                data = self.socket.recv(1024)
            except OSError:
                self.is_failed = True
                return
        
            if len(data) == 0:
                self.is_closed = True
                return
            else:
                return data
        else:
            return NetworkSocketHandling(self.socket.accept()[0], True, True)

    def register(self, on_readable, on_exception, on_connected, on_closed, on_failure):
        S.getNEP(S.loc.tcb).addSock(self, on_connected, on_readable, on_closed, on_failure, on_exception)
       
    def write(self, data):
        if not self.is_client:
            raise ValueError('Server socket does not support writes!')
        
        # Attempt speculative execution
        self.writebuf.extend(data)
        try:
            # following two lines replaced this one due to transient BufferErrors
            # del self.writebuf[:self.socket.send(self.writebuf)]
            dsl = self.socket.send(self.writebuf)
            self.writebuf = self.writebuf[dsl:]
        except BlockingIOError:
            pass
        except IOError:
            try:
                self.socket.close()
            except:
                pass
            self.is_failed = True
            self.is_closed = True

    def close(self):
        if len(self.writebuf) > 0:
            self.close_on_all_write = True
        else:
            try:
                self.socket.close()
            except OSError:
                self.is_failed = True
            
    def fileno(self) -> int:
        return self._fileno
            
import yos.io
yos.io.NetworkSocket = NetworkSocketHandling