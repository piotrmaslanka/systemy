from yos.rt import BaseTasklet
from yos.tasklets import Tasklet
from yos.io import NetworkSocket


class BabyTasklet(BaseTasklet):
    
    def on_startup(self):
        print("Baby here!")


class HelloWorldTasklet(BaseTasklet):

    def on_startup(self):
        print('Hello World!')
        
        Tasklet.start(BabyTasklet, 'baby', None, None, self.on_spawned)
        
    def on_spawned(self, baby):
        print("Baby spawned!")
    
    