import threading, queue
from ypage.nukleon.structs import TaskletControlBlock
from ypage.nukleon import S
from ypage.interfaces import Processor

class EEP(threading.Thread, Processor):
    def __init__(self):
        threading.Thread.__init__(self)
        
        self.events_to_process = queue.Queue()
        self.terminated = False
        
    def terminate(self):
        """
        Signal this thread to terminate
        """
        self.terminated = True
        
    def put(self, tcb: TaskletControlBlock, callable_: callable, *args, **kwargs):
        """Puts an event to execute into the queue"""
        self.events_to_process.put((tcb, callable_, args, kwargs))
        tcb.pending += 1
        
    def onTaskletTerminated(self, tcb: TaskletControlBlock):
        # I an the Event Processor
        # I do not need to do anything - tcb entries have their is_alive set to False
        # which will get automatically ignored by the runtime.
        pass
        
    def run(self):
        while not self.terminated:
            
            try:
                tcb, callable_, args, kwargs = self.events_to_process.get(True, 10)
            except queue.Empty:
                continue
            
            if tcb.is_alive:
                S.loc.tcb = tcb
                callable_(*args, **kwargs)
                tcb.pending -= 1
        
                if tcb.shouldBeCollected():
                    tcb.is_alive = False
                    S.onTaskletTerminated(tcb)
    