from yos.rt import BaseTasklet
from yos.tasklets import Tasklet
from yos.io import NetworkSocket

class HelloWorldTasklet(BaseTasklet):

    def on_startup(self):
        print('Hello World!')
    
    