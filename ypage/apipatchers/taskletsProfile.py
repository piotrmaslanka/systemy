import yos.tasklets
from ypage.nukleon import S
import threading

class Profile(yos.tasklets.Profile):
    """
    Class used to tell runtime about execution profile of current tasklet
    """
    
    @staticmethod
    def disable_gc():
        S.loc.tcb.is_gc_on = False
        
    @staticmethod
    def enable_gc():
        S.loc.tcb_is_gc_on = True
        
    @staticmethod
    def is_gc_enabled():
        return S.loc.tcb.is_gc_on
    
yos.tasklets.Profile = Profile