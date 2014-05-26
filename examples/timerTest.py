from yos.rt import BaseTasklet
from yos.time import Timer


class PulserTasklet(BaseTasklet):
    
    def on_startup(self):
        Timer.create(1, self.pulser)
        
        
    def pulser(self):
        print("Pulse!")
        Timer.create(1, self.pulser)