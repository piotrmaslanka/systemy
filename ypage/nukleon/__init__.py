from threading import Lock, local
from queue import Queue

from ypage.nukleon.NewTIDIssuer import NewTIDIssuer

class S(object):
    """
    The grand central dispatch
    """
    
    syslock = Lock()
    
    
    tcbs = {}   # tid: int -> TaskletControlBlock
    
    terminations = Queue()  # list of tids'


    tidIssuer = NewTIDIssuer()

    loc = local()


    eeps = []       # event processors
    
    
    @staticmethod
    def registerNewTasklet(tcb):
        S.tcbs[tcb.tid] = tcb
    
    @staticmethod
    def onTaskletTerminated(tcb):
        """an EEP has decided that a tasklet is dead"""
        
    
    
    @staticmethod
    def startup():
        """Starts up the SIC"""
      
        from ypage.eep import EEP
        eep1 = EEP()
        eep2 = EEP()
         
        eep1.start()      
        eep2.start()
       
        S.eeps.append(eep1)
        S.eeps.append(eep2)
        
    @staticmethod
    def schedule(tcb, callable_: callable, *args, **kwargs):
        """Schedule an event on one of available EEPs"""
        S.eeps[tcb.tid % len(S.eeps)].put(tcb, callable_, *args, **kwargs)

    @staticmethod
    def getNextTID() -> int:
        """Returns a new, free TID"""
        return S.tidIssuer.next()