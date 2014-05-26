"""Synchronous Message Processor"""
import threading, time, queue
from ypage.nukleon import S
from ypage.nukleon.NewIDIssuer import NewIDIssuer
from ypage.interfaces import Processor
import heapq

class TEP(threading.Thread, Processor):
    def __init__(self, coreno):
        threading.Thread.__init__(self)
        
        self.terminated = False
        
        self.metalock = threading.RLock()
        
        self.events = []    # a heap queue of (run_at, Handler)
        
        self.pending_terminations = queue.Queue() # queue of tcbs
        
        self.teidgen = NewIDIssuer() # timer event ID, unique per TEP

    def terminate(self):
        self.terminated = True

    def onTaskletTerminated(self, tcb):
        self.pending_terminations.put(tcb)

    def register(self, timerHandler):
        """Called by tasklets when they want to register a handler"""
        with self.metalock:
            heapq.heappush(self.events, (timerHandler.run_at, timerHandler))
        S.loc.tcb.handlers += 1

    def cancel(self, timerHandler):
        """Called by tasklets when they want to cancel a handler"""
        # TODO: this is just a hack. This does nothing, as 
        # main thread always checks for .cancelled flag, which handlers set...

    def run(self):
        while not self.terminated:
            time.sleep(1)
            
            with self.metalock:
                try:
                    now = time.time()
                    while self.events[0][0] < now:
                        handler = heapq.heappop(self.events)[1]
                        if not handler.cancelled:
                            S.schedule(handler.tcb, handler.callback)
                        handler.tcb.handlers -= 1       # TODO: race condition?
                except IndexError:
                    pass

            while self.pending_terminations.qsize() > 0:
                term = self.pending_terminations.get()
                with self.metalock:
                    events = []
                    for rat, handler in self.events:
                        if handler.tcb != term:
                            events.append((rat, handler))

                    heapq.heapify(events)
                    self.events = events