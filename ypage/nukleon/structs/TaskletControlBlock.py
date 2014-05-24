class TaskletControlBlock(object):
    """
    A control block for tasklets
    """
    
    def __init__(self, tid: int, user: str, group: str, name: str):
        
        self.tid = tid
        self.user = user
        self.group = group
        self.name = name
        
        self.handlers = 0
        self.pending = 0
        self.is_gc_on = False
        self.is_alive = True
        
    def shouldBeCollected(self) -> bool:
        """Returns whether it should be removed from the system"""
        if self.is_gc_on:
            return self.handlers == self.pending == 0
        else:
            return not self.is_alive
        
    def __eq__(self, tcb) -> bool:
        return self.tid == tcb.tid
    
    def __hash__(self):
        return hash(self.tid)