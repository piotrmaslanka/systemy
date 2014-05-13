from yos.io import NetworkSocket
from yos.rt import BaseTasklet
from yos.tasklets import Tasklet

class NetworkTest(BaseTasklet):
    
    def on_startup(self):
        self.sock = NetworkSocket.client(NetworkSocket.SOCK_TCP, ('www.yahoo.com', 80))
        self.sock.register(self.on_readable, None, self.on_connected, self.on_end, self.on_end)

    def on_readable(self, sock, data):
        print("NT: Received", len(data), "bytes")
        
    def on_connected(self, sock):
        print("NT: Connected, sending HTTP request")
        sock.write(b'GET / HTTP/1.1\nHost: www.yahoo.com\nContent-Type: text/html; charset=utf-8\n\n')
        
    def on_end(self, sock):
        print("NT: Socket disposed of")