from yos.tasklets import Tasklet
from threading import RLock

from ydrp import globals

class TaskletControlBlock(object):
    def __init__(self, tid, group, name, user):
        self.tid = tid
        self.group = group
        self.name = name
        self.user = user

class ySAP(object):
    def __init__(self):
        self.tcbs = {}      # TID => TCB
        self.tasklets = {}  # TID => Tasklet instance
        self.next_tid = 1
        
        self.tcb_manip_lock = RLock()
        
    def _getNextTID(self):
        with self.tcb_manip_lock:
            nexttid = self.next_tid
            self.next_tid += 1
            return nexttid

globals.ySAP = ySAP()
            
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
        
        tid = globals.ySAP._getNextTID()
        tcb = TaskletControlBlock(tid, 
                                  current_tcb.group,
                                  current_tcb.name,
                                  current_tcb.user)

        with globals.ySAP.tcb_manip_lock:
            globals.ySAP.tcbs[tid] = tcb
            globals.ySAP.tasklets[tid] = task
            
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
        @param result1 callable/1 to call with Tasklet or specific exception class
        """
        with globals.ySAP.tcb_manip_lock:
            if tid not in globals.ySAP.tasklets:
                raise yos.tasklets.Tasklet.DoesNotExist
            
            tcb = globals.ySAP.tcbs[tid]

        globals.yEEP.put(globals.loc.current_tcb, result1, TaskletManagingLibrary(tid, 
                                                                                tcb.group, 
                                                                                tcb.name, 
                                                                                tcb.user))            
    
            
        
    def send(self, obj, result1=None):
        """
        Sends given tasklet an object without blocking
        
        There's no guarantee that it will arrive, as this is asynchronous
        
        @param obj Object to send
        @param result1 callable/1 that will be passed a boolean on whether the call succeeded
        @raise AccessDenied not allowed to send
        """
        source_tcb = globals.loc.current_tcb

        with globals.ySAP.tcb_manip_lock:
            if self.tid not in globals.ySAP.tasklets:
                raise yos.tasklets.Tasklet.DoesNotExist
            
            target_tcb = globals.ySAP.tcbs[self.tid]
            target_task = globals.ySAP.tasklets[self.tid]

        globals.yEEP.put(target_tcb, target_task.on_message, source_tcb.tid, obj)
        if result1 != None:     
            globals.yEEP.put(source_tcb, result1, True)     
    
    @staticmethod
    def sendto(tid, obj, result1=None):
        """
        Sends an object to a tasklet specified by it's TID
        
        @param tid TID of recipient tasklet
        @param obj Object to send
        @param result1 callable/1 that will be passed a boolean on whether the call succeeded
        @raise AccessDenied not allowed to send
        """            
        source_tcb = globals.loc.current_tcb

        with globals.ySAP.tcb_manip_lock:
            if tid not in globals.ySAP.tasklets: 
                raise yos.tasklets.Tasklet.DoesNotExist
            
            target_tcb = globals.ySAP.tcbs[tid]
            target_task = globals.ySAP.tasklets[tid]

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
        
import yos.tasklets
yos.tasklets.Tasklet = TaskletManagingLibrary