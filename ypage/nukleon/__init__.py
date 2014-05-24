from threading import Lock, local
from queue import Queue

from ypage.nukleon.NewTIDIssuer import NewTIDIssuer

class S(object):
    """
    The grand central dispatch
    """
    
    frameNo = 0
    pageNo = 0
    
    syslock = Lock()
    
    tcbs = {}   # tid: int -> TaskletControlBlock
    tcb_inst = {}    # tid: int -> TaskletInstance
    
    terminations = Queue()  # list of tids'


    tidIssuer = NewTIDIssuer()

    loc = local()


    eeps = []       # event processors
    
    
    @staticmethod
    def registerNewTasklet(tcb, inst):
        S.tcbs[tcb.tid] = tcb
        S.tcb_inst[tcb.tid] = inst
    
    @staticmethod
    def onTaskletTerminated(tcb):
        """an EEP has decided that a tasklet is dead"""
        del S.tcbs[tcb.tid]
        del S.tcb_inst[tcb.tid]
    
    @staticmethod
    def startup():
        """Starts up the SIC"""
        from ypage.eep import EEP
        eep1 = EEP()
        eep1.start()             
        S.eeps.append(eep1)
        
    @staticmethod
    def schedule(tcb, callable_: callable, *args, **kwargs):
        """Schedule an event on one of available EEPs"""
        S.eeps[tcb.tid % len(S.eeps)].put(tcb, callable_, *args, **kwargs)


    @staticmethod
    def isLocal(tid: int) -> bool:
        """Checks if a particular TID belongs to a local tasklet"""
        return (tid >> 40) == ((S.frameNo << 8) + S.pageNo)

    @staticmethod
    def getNextTID() -> int:
        """Returns a new, free TID"""
        return S.tidIssuer.next()