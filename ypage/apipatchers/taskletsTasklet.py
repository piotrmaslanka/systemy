import yos.tasklets
from ypage.nukleon import S
from ypage.nukleon.structs import TaskletControlBlock

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
        
        S.registerNewTasklet(tcb)
        S.schedule(tcb, task.on_startup)

        if result1 != None:
            S.schedule(current_tcb, result1, Tasklet(tid, newuser, newgroup, newname))
        
    @staticmethod
    def open(tid, result1):
        pass
        
    def send(self, obj, result1=None):
        pass

    @staticmethod
    def send_to(tid, obj, result1=None):
        pass
    
yos.tasklets.Tasklet = Tasklet