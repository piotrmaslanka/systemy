"""
Server that echoes everything sent to it via TCP
"""
from yos.rt import BaseTasklet
from yos.tasklets import Tasklet
from yos.io import NetworkSocket

class MultiTaskletServerTasklet(BaseTasklet):
    """Server that uses multiple slave tasklets to do it's job"""

    class ClientTasklet(BaseTasklet):
        def __init__(self, clientSocket):
            self.clientSocket = clientSocket
            
        def on_startup(self):
            self.clientSocket.register(self.on_readable, None, None, None, None)
            
        def on_readable(self, sock, data):
            sock.write(data)            
    
    def on_startup(self):
        self.serverSocket = NetworkSocket.server(NetworkSocket.SOCK_TCP, ('127.0.0.1', 65000))
        self.serverSocket.register(self.on_readable, None, None, None, None)

    def on_readable(self, sock, newconn):
        Tasklet.start(MultiTaskletServerTasklet.ClientTasklet, None, newconn)
        
        
class SingleTaskletServerTasklet(BaseTasklet):
    """Server that uses a single tasklet to do it's job"""
    
    def on_startup(self):
        NetworkSocket.server(NetworkSocket.SOCK_TCP, ('127.0.0.1', 65000)).register(self.on_new_connection, None, None, None, None)

    def on_new_connection(self, sock, newconn):
        newconn.register(self.on_client_data, None, None, None, None)
        
    def on_client_data(self, sock, data):
        sock.write(data) 


