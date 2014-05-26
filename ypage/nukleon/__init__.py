from threading import Lock, local
from queue import Queue
import itertools
from ypage.nukleon.NewIDIssuer import NewIDIssuer

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


    tidIssuer = NewIDIssuer()

    loc = local()


    eeps = []       # event processors
    neps = []       # network processors
    smps = []       # synchronous message processors
    teps = []       # time event processors
    
    @staticmethod
    def registerNewTasklet(tcb, inst):
        S.tcbs[tcb.tid] = tcb
        S.tcb_inst[tcb.tid] = inst
    
    @staticmethod
    def onTaskletTerminated(tcb):
        """an EEP has decided that a tasklet is dead"""
        del S.tcbs[tcb.tid]
        del S.tcb_inst[tcb.tid]
        
        for proc in itertools.chain(S.eeps, S.neps, S.smps, S.teps):
            proc.onTaskletTerminated(tcb)

    @staticmethod
    def startup(eeps=3, neps=3, smps=2, teps=2):
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
            
        from ypage.processors.SMP import SMP
        for i in range(0, smps):
            smp = SMP(i)
            smp.start()
            S.smps.append(smp)
        
        from ypage.processors.TEP import TEP
        for i in range(0, teps):
            tep = TEP(i)
            tep.start()
            S.teps.append(tep)
        
        print("Started", eeps+neps+smps+teps, "processors total:")
        print("   ", neps, "Network Event Processors")
        print("   ", eeps, "Event Execution Processors")
        print("   ", smps, "Synchronous Message Processors")
        print("   ", teps, "Time Event Processors")
        
    @staticmethod
    def getNEP(tcb):
        """Returns a NEP that handles given tasklet"""
        return S.neps[tcb.tid % len(S.neps)]

    @staticmethod
    def getSMP(tid):
        """Returns a SMP that handles given tasklet on behalf of tid"""
        return S.smps[tid % len(S.smps)]

    @staticmethod
    def getTEP(tid):
        """Returns a TEP that handles given tasklet on behalf of tid"""
        return S.teps[tid % len(S.teps)]
        
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