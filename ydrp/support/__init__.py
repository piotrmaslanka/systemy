from yos.rt import BaseTasklet
from yos.tasklets import Tasklet
from yos.io import NetworkSocket

class SupportElementTasklet(BaseTasklet):

    def on_startup(self):
        NetworkSocket.server(NetworkSocket.SOCK_TCP, ('0.0.0.0', 1000)) \
            .register(self.on_new_connection, None, None, None, None)
        
    def on_new_connection(self, serversocket, newsocket):
        Tasklet.start(ClientPointTasklet(newsocket), newname='client')
    
    
class ClientPointTasklet(BaseTasklet):
    def __init__(self, clientsock):
        self.client = clientsock
        
    def on_startup(self):
        self.client.register(self.on_readed, None, None, None, None)
        self.client.write('''
 _  _   _  _____  ___ 
( \/ ) / )(  _  )/ __)
 \  / / /  )(_)( \__ \
 (__)(_/  (_____)(___/)
 
  Support Element v0.1
  
  
>''')
        
    def on_readed(self, sock, data):
        pass    