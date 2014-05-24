import yos.tasklets
from ypage.nukleon import S
from ypage.nukleon.structs import TaskletControlBlock
from yos.rt import GCTasklet

class Tasklet(yos.tasklets.Tasklet):
    
    
    def __init__(self, tid, user, group, name):
        self.tid = tid
        self.user = user
        self.group = group
        self.name = name
    
    @staticmethod
    def me():
        tcb = S.loc.tcb
        return Tasklet(tcb.tid, tcb.user, tcb.group, tcb.name)
    
    @staticmethod
    def start(taskletCls, newname='Tasklet', newgroup=None, newuser=None, result1=None, *args, **kwargs):
        task = taskletCls(*args, **kwargs)
        
        current_tcb = S.loc.tcb
        
        if (newuser != None) and (current_tcb.user != 'SYSTEMYA'):
            raise Tasklet.AccessDenied('Cannot set user, not SYSTEMYA')
        newuser = newuser or current_tcb.user
        if (newgroup != None) and (current_tcb.group != 'admin'):
            raise Tasklet.AccessDenied('Cannot set group, not admin')
        newgroup = newgroup or current_tcb.group
        
        tid = S.getNextTID()
        tcb = TaskletControlBlock(tid, newuser, newgroup, newname)
        
        if isinstance(task, GCTasklet):
            tcb.is_gc_on = True
        
        S.registerNewTasklet(tcb, task)
        S.schedule(tcb, task.on_startup)

        if result1 != None:
            S.schedule(current_tcb, result1, Tasklet(tid, newuser, newgroup, newname))

    @staticmethod
    def open(tid, result1):
        if not S.isLocal(tid):
            raise NotImplementedError("Sorry, no IPC yet")
        
        current_tcb = S.loc.tcb
        
        try:
            tcb = S.tcbs[tid]
            if not tcb.is_alive:
                raise KeyError
                
        except KeyError:
            S.schedule(current_tcb, result1, Tasklet.DoesNotExist)
        else:
            S.schedule(current_tcb, result1, Tasklet(tcb.tid, tcb.user, tcb.group, tcb.name))
        
    def send(self, obj, result1=None):
        current_tcb = S.loc.tcb
        
        try:
            tcb = S.tcbs[self.tid]

            if not tcb.is_alive:
                raise KeyError
            tcb_inst = S.tcb_inst[self.tid]
        except KeyError:
            if result1 != None:
                S.schedule(current_tcb, result1, Tasklet.DoesNotExist)
        else:
            S.schedule(tcb, tcb_inst.on_message, current_tcb.tid, obj)
            if result1 != None:
                S.schedule(current_tcb, result1, True)

    @staticmethod
    def send_to(tid, obj, result1=None):
        if not S.isLocal(tid):
            raise NotImplementedError("Sorry, no IPC yet")
        
        current_tcb = S.loc.tcb
        
        try:
            tcb = S.tcbs[tid]
            if not tcb.is_alive:
                raise KeyError
            tcb_inst = S.tcb_inst[tid]
        except KeyError:
            if result1 != None:
                S.schedule(current_tcb, result1, Tasklet.DoesNotExist)
        else:
            if result1 != None:
                S.schedule(current_tcb, result1, Tasklet(tcb.tid, tcb.user, tcb.group, tcb.name))
            S.schedule(tcb, tcb_inst.on_message, current_tcb.tid, obj)
    
yos.tasklets.Tasklet = Tasklet