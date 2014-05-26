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
        
        # Temporarily disable TCB, so that calling tasklet's context
        # is not used for misled API calls
        # essentially bug-prevention
        prev_tcb = S.loc.tcb
        S.loc.tcb = None
        
        task = taskletCls(*args, **kwargs)
        
        S.loc.tcb = prev_tcb
        
        current_tcb = prev_tcb
        
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
    def open(tid: int, result1: callable):
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
        
    def send(self, obj: object, result1: int=None):
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
    def send_to(tid, obj: object, result1: callable=None):
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

    def terminate(self, result1=None):
        if self.user == 'SYSTEMYA':
            if result1 != None:
                S.schedule(S.loc.tcb, result1, Tasklet.AccessDenied)
        
        try:
            tcb = S.tcbs[self.tid]
            if not tcb.is_alive:
                raise KeyError
        except KeyError:
            if result1 != None:
                S.schedule(S.loc.tcb, result1, Tasklet.DoesNotExist)
        else:
            # OK, we got the tasklet, kill'em
            if result1 != None:
                if S.loc.tcb != tcb:
                    S.schedule(S.loc.tcb, result1, True)
                
            S.onTaskletTerminated(tcb)

    def send_sync(self, obj: object, result1: callable):
        S.getSMP(S.loc.tcb.tid).send_sync_to(S.loc.tcb, self.tid, obj, result1)
        
    @staticmethod
    def send_sync_to(tid: int, obj: object, result1: callable):
        if not S.isLocal(tid):
            raise NotImplementedError("Sorry, no IPC yet")
        
        S.getSMP(S.loc.tcb.tid).send_sync_to(S.loc.tcb, tid, obj, result1)

    
yos.tasklets.Tasklet = Tasklet