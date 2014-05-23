from yos.rt import BaseTasklet
from yos.tasklets import Tasklet
from yos.io import NetworkSocket


class BabyTasklet(BaseTasklet):
    
    def on_startup(self):
        me = Tasklet.me()
        print('I\'m the baby! My name is %s.%s.%s, TID is %s' % (me.user, me.group, me.name, me.tid))


class HelloWorldTasklet(BaseTasklet):

    def on_startup(self):
        me = Tasklet.me()
        print('Hello World! My name is %s.%s.%s, TID is %s' % (me.user, me.group, me.name, me.tid))
        
        Tasklet.start(BabyTasklet, 'baby', None, None, self.on_spawned)
        
    def on_spawned(self, baby):
        print("Baby spawned! It's name is %s.%s.%s, TID is %s" % (baby.user, baby.group, baby.name, baby.tid))
    