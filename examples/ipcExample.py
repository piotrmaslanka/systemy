from yos.rt import BaseTasklet
from yos.tasklets import Tasklet, Profile
from yos.io import NetworkSocket


class WorkerTasklet(BaseTasklet):
    
    def on_message(self, source, number):
        Tasklet.send_to(source, number ** 2)
        

class IPCTasklet(BaseTasklet):

    def on_startup(self):
        Tasklet.start(WorkerTasklet, 'baby', None, None, self.on_spawned)
        
    def on_spawned(self, baby):
        baby.send(4)
        
    def on_message(self, source, number):
        print("4 squared is", number)