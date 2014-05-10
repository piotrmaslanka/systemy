from yos import YOSException

class NetworkSocket(object):
    """
    Defines a network socket
    """
    
    SOCK_TCP = 0
    SOCK_UDP = 1
    SOCK_TCPv6 = 2
    SOCK_UDPv6 = 3
    SOCK_PIPE = 4
    
    class SocketException(YOSException):
        """Base class for socket exceptions"""
        
    @staticmethod
    def client(socktype, address):
        """Establishes a connection to target client at specified address.
        @param socktype Type of the socket
        @param address Socket-dependent address to target
        @return NetworkSocket a socket in connecting state
        """
        
    @staticmethod
    def server(socktype, address):
        """Establishes a server to listen at specified address.
        @param socktype Type of the socket
        @param address Socket-dependent address to target
        @return NetworkSocket a socket in connecting state
        """
        
    def register(self, on_readable, on_exception, on_connected, on_closed, on_failure):
        """
        Register the socket in I/O processing layer. Nonblocking.
        
        Every socket will have on_connected called exactly one time
        
        @param on_readable callable/2 called in there's inbound data for socket. Parameter will be this socket
                            and readed data
        @param on_exception callable/1 called if socket's in exception status. Parameter will be this socket
        @param on_connected callable/1 called if socket's got connected. Parameter will be this socket of exception
                            class if connect fails
        @param on_closed callable/1 called if socket is gracefully closed. Parameter will be this socket
        @param on_failure callable/1 called if socket unexpectedly fails. Parameter will be this socket
        """
        
    def write(self, data):
        """
        Queues data to be written (stream or datagram). Nonblocking.
        
        @param data data to be written
        @type data bytes or bytearray
        """
        
        
    def close(self):
        """
        Order this socket to close. Closing will be reported by .register's handlers. Nonblocking.
        """