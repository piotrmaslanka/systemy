from yos.rt import BaseTasklet
from yos.tasklets import Tasklet

class TerminationExampleTasklet(BaseTasklet):

    def on_startup(self):
        Tasklet.start(ChildTasklet, None, None, None, self.on_child_open)
    
    def on_child_open(self, child):
        child.terminate()
        Tasklet.me().terminate()
    
    
class ChildTasklet(BaseTasklet):
    pass