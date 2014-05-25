from ypage.nukleon import S

import ypage.apipatchers    # this fixes yos module imports

from ypage.nukleon.structs import TaskletControlBlock
from ypage.initrd import initrd
from yos.rt import GCTasklet
from yos.tasklets import Tasklet
import time
import importlib

class InitTasklet(GCTasklet):
    def __init__(self, initlist):
        self.initlist = initlist
        
    def on_startup(self):
        print ("INIT: Init v1.0 (part of System y) started")
        for elem in self.initlist:
            if len(elem) == 4: user, group, name, cls = elem; args = (); kwargs = {}
            if len(elem) == 5: user, group, name, cls, args = elem; kwargs = {}
            if len(elem) == 6: user, group, name, cls, args, kwargs = elem
            
            if isinstance(cls, str):    
                # attempt an import
                try:
                    mod = importlib.import_module('.'.join(cls.split('.')[:-1]))
                    cls = getattr(mod, cls.split('.')[-1])
                except ImportError:
                    print("INIT: Failed to import", cls)
                    continue
                
            Tasklet.start(cls, name, group, user, None, *args, **kwargs) 

            print("INIT:", len(self.initlist), "tasklets spawned, exiting")

if __name__ == '__main__':
    S.startup()
    S.tidIssuer.adjustID(0)  # 0th Page on 0th Frame

    
    # manual bootstrap here
    init = InitTasklet(initrd)
    tcb = TaskletControlBlock(0, 'SYSTEMYA', 'admin', 'init')
    S.registerNewTasklet(tcb, init)
    S.schedule(tcb, init.on_startup)    

