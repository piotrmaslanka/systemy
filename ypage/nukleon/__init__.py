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
    neps = []       # network processors
    
    @staticmethod
    def registerNewTasklet(tcb, inst):
        S.tcbs[tcb.tid] = tcb
        S.tcb_inst[tcb.tid] = inst
    
    @staticmethod
    def onTaskletTerminated(tcb):
        """an EEP has decided that a tasklet is dead"""
        del S.tcbs[tcb.tid]
        del S.tcb_inst[tcb.tid]
        
        for eep in S.eeps:
            eep.onTaskletTerminated(tcb)
        for nep in S.neps:
            nep.onTaskletTerminated(tcb)
    
    @staticmethod
    def startup(eeps=3, neps=3):
        """Starts up the SIC"""
        from ypage.processors.EEP import EEP
        for i in range(0, eeps):
            eep = EEP()
            eep.start()             
            S.eeps.append(eep)
        
        from ypage.processors.NEP import NEP
        for i in range(0, neps):
            nep = NEP()
            nep.start()
            S.neps.append(nep)
        
        print("Started", len(S.neps)+len(S.eeps), "processors total:")
        print("   ", len(S.neps), "Network Event Processors")
        print("   ", len(S.eeps), "Event Execution Processors")
        
    @staticmethod
    def getNEP(tcb):
        """Returns a NEP that handles given tasklet"""
        return S.neps[tcb.tid % len(S.neps)]
        
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