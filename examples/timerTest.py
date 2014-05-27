from yos.rt import BaseTasklet
from yos.time import Timer


class PulserTasklet(BaseTasklet):
    
    def on_startup(self):
        Timer.schedule(1, self.pulser)
        self.apulser_scheduler = Timer.repeat(1, self.apulser)
        
        self.apulser_count = 10
    def apulser(self):
        print("Pulse, repeat")
        self.apulser_count -= 1
        
        if self.apulser_count == 0:
            print("10 times apulser, cancelling")
            self.apulser_scheduler.cancel()

    def pulser(self):
        print("Pulse, sync!")
        Timer.schedule(1, self.pulser)