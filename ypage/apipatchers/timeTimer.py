from yos.time import Timer
from ypage.nukleon import S
import time

class TimerHandler(Timer):
    
    @staticmethod
    def create(run_in, callback):
        self = TimerHandler.__new__(TimerHandler)
        self.__tep = S.getTEP(S.loc.tcb.tid)
        
        # following accessible to TEP
        self.tcb = S.loc.tcb
        self.teid = self.__tep.teidgen.next()
        self.callback = callback
        self.run_at = time.time() + run_in
        self.cancelled = False
        
        self.__tep.register(self)
        
        return self
    
    def cancel(self):
        self.cancelled = True
        self.__tep.cancel(self)

import yos.time
yos.time.Timer = TimerHandler