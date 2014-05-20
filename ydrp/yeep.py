"""y Event Execution Processor"""
from queue import Queue, Empty
from threading import Thread

from ydrp import globals

class yEEP(Thread):
    def __init__(self):
        self.events = Queue()
        self.terminated = False
        Thread.__init__(self)
        
    def terminate(self):
        self.terminated = True
        
    def run(self):
        while not self.terminated:
            try:
                tcb, f, a, k = self.events.get(True, 10)
            except Empty:
                continue
            
            globals.loc.current_tcb = tcb
            
            if tcb.is_alive:
                f(*a, **k)
            
            tcb.pending -= 1
            
            if tcb.handlers == tcb.pending == 0:
                globals.SysRTI.taskletExpired(tcb)
    
    def put(self, tcb, handler, *args, **kwargs):
        tcb.pending += 1
        self.events.put((tcb, handler, args, kwargs))
        
globals.yEEP = yEEP()