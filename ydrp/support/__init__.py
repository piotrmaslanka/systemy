from yos.rt import BaseTasklet
from yos.tasklets import Tasklet
from yos.io import NetworkSocket

class NetworkTest(BaseTasklet):
    
    def on_startup(self):
        self.sock = NetworkSocket.client(NetworkSocket.SOCK_TCP, ('www.yahoo.com', 80))
        self.sock.register(self.on_readable, None, self.on_connected, self.on_end, self.on_end)

    def on_readable(self, sock):
        print("NT: Received data, total %s bytes in" % (len(sock.readbuf), ))
        
    def on_connected(self, sock):
        print("NT: Connected, sending HTTP request")
        sock.write(b'GET / HTTP/1.1\nHost: www.yahoo.com\nContent-Type: text/html; charset=utf-8\n\n')
        
    def on_end(self, sock):
        print("NT: Socket disposed of")

class LaunchedTest(BaseTasklet):
    
    def on_startup(self):
        print("LT: Hey, I was launched! My TID is", Tasklet.me().tid)
        
        self.already_replied = False

    def on_message(self, src, msg):
        print("LT: Received %s from %s" % (msg, src))
        
        if not self.already_replied:        
            Tasklet.open(src, lambda tasklet: tasklet.send('And hello you back!'))
            self.already_replied = True

class SupportElementTasklet(BaseTasklet):

    def on_startup(self):
        
        print("SET: Hey, I was started! My TID is", Tasklet.me().tid)
        
        def on_child_started(child):
            child.send('Hello World, Child!')
            Tasklet.sendto(child.tid, 'Hello World Child by sendto')
        
        def on_invalid_child_open(child):
            if child is Tasklet.DoesNotExist:
                print("SET: tried to open a bad child and it didn't open :)")
        
        Tasklet.start(LaunchedTest, on_child_started)
        Tasklet.me().send('Hello Me!')
        Tasklet.open(100, on_invalid_child_open)
        
        Tasklet.start(NetworkTest)

    def on_message(self, src, msg):
        print("SET: Received %s from %s" % (msg, src))
