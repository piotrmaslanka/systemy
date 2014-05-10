from yos.rt import BaseTasklet
from yos.tasklets import Tasklet


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
        
        def send_to_child(child):
            child.send('Hello World, Child!')
            Tasklet.sendto(child.tid, 'Hello World Child by sendto')
        
        Tasklet.start(LaunchedTest, send_to_child)
        Tasklet.me().send('Hello Me!')

    def on_message(self, src, msg):
        print("SET: Received %s from %s" % (msg, src))
