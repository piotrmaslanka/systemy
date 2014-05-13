from yos.tasklets import Tasklet, Profile
from threading import RLock

from ydrp import globals

"""
Majority of functions here do not modify tasklet's handlers.
If they were network-based, they should have done so
"""

class TaskletControlBlock(object):
    def __init__(self, tid, group, name, user):
        self.tid = tid
        self.group = group
        self.name = name
        self.user = user
        
        self.handlers = 0
        self.pending = 0
    

class SysRTI(object):
    def __init__(self):
        self.tcbs = {}      # TID => TCB
        self.tasklets = {}  # TID => Tasklet instance
        self.next_tid = 1
        
        self.tcb_manip_lock = RLock()
        
    def taskletExpired(self, tcb):    
        with self.tcb_manip_lock:
            del self.tcbs[tcb.tid]
            del self.tasklets[tcb.tid]
            print("Tasklet TID=%s expired" % (tcb.tid, ))
        
    def _getNextTID(self):
        with self.tcb_manip_lock:
            nexttid = self.next_tid
            self.next_tid += 1
            return nexttid

globals.SysRTI = SysRTI()
            
class TaskletManagingLibrary(Tasklet):
    
    def __init__(self, tid, group, name, user):
        self.tid = tid
        self.group = group
        self.name = name
        self.user = user
    
    @staticmethod
    def start(taskletCls, result1=None, *args, **kwargs):
        task = taskletCls(*args, **kwargs)
        
        current_tcb = globals.loc.current_tcb
        
        tid = globals.SysRTI._getNextTID()
        tcb = TaskletControlBlock(tid, 
                                  current_tcb.group,
                                  current_tcb.name,
                                  current_tcb.user)

        print("Started new tasklet, TID=%s" % (tid, ))

        with globals.SysRTI.tcb_manip_lock:
            globals.SysRTI.tcbs[tid] = tcb
            globals.SysRTI.tasklets[tid] = task
            
        globals.yEEP.put(tcb, task.on_startup)
        if result1 != None:
            globals.yEEP.put(current_tcb, result1, TaskletManagingLibrary(tid, 
                                                                           current_tcb.group, 
                                                                           current_tcb.name, 
                                                                           current_tcb.user))
    @staticmethod
    def open(tid, result1):
        """
        Returns an object representing target tasklet
        
        @param tid Tasklet Identifier
        @param result1 callable/1 to call with Tasklet or specific exception class if it fails
        """
        try:
            with globals.SysRTI.tcb_manip_lock:            
                tcb = globals.SysRTI.tcbs[tid]
        except KeyError:
            if result1 != None:
                globals.yEEP.put(globals.loc.current_tcb, result1, yos.tasklets.Tasklet.DoesNotExist)
        else:
            globals.yEEP.put(globals.loc.current_tcb, result1, TaskletManagingLibrary(tid, 
                                                                                    tcb.group, 
                                                                                    tcb.name, 
                                                                                    tcb.user))            
    
            
        
    def send(self, obj, result1=None):
        """
        Sends given tasklet an object without blocking
        
        There's no guarantee that it will arrive, as this is asynchronous
        
        @param obj Object to send
        @param result1 callable/1 that will be passed a True whether the call succeeded
               of exception class if it doesn't
        """
        source_tcb = globals.loc.current_tcb

        with globals.SysRTI.tcb_manip_lock:
            if self.tid not in globals.SysRTI.tasklets:
                if result1 != None:
                    globals.yEEP.put(source_tcb, result1, yos.tasklets.Tasklet.DoesNotExist)
                return
            
            target_tcb = globals.SysRTI.tcbs[self.tid]
            target_task = globals.SysRTI.tasklets[self.tid]

        globals.yEEP.put(target_tcb, target_task.on_message, source_tcb.tid, obj)
        if result1 != None:     
            globals.yEEP.put(source_tcb, result1, True)     
    
    @staticmethod
    def send_to(tid, obj, result1=None):
        """
        Sends an object to a tasklet specified by it's TID
        
        @param tid TID of recipient tasklet
        @param obj Object to send
        @param result1 callable/1 that will be passed a True whether the call succeeded
               of exception class if it doesn't
        """            
        source_tcb = globals.loc.current_tcb

        with globals.SysRTI.tcb_manip_lock:
            if tid not in globals.SysRTI.tasklets: 
                if result1 != None:
                    globals.yEEP.put(source_tcb, result1, yos.tasklets.Tasklet.DoesNotExist)
                return
            
            target_tcb = globals.SysRTI.tcbs[tid]
            target_task = globals.SysRTI.tasklets[tid]

        globals.yEEP.put(target_tcb, target_task.on_message, source_tcb.tid, obj)
        if result1 != None:
            globals.yEEP.put(source_tcb, result1, True)    
                
    @staticmethod
    def me():
        """
        Returns Tasklet object that represents the caller.
        Does not block
        @return yos.tasklets.Tasklet representing the caller
        """
        tcb = globals.loc.current_tcb
        return TaskletManagingLibrary(tcb.tid, tcb.group, tcb.name, tcb.user)     

class ProfileHandler(Profile):
    @staticmethod
    def disable_gc():
        globals.loc.current_tcb.handlers += 1
        
    @staticmethod
    def enable_gc():
        globals.loc.current_tcb.handlers -= 1      
        
import yos.tasklets
yos.tasklets.Tasklet = TaskletManagingLibrary
yos.tasklets.Profile = ProfileHandler