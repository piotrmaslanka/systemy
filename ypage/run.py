from ypage.nukleon import S

import ypage.apipatchers    # this fixes yos module imports

from examples.HelloWorld import HelloWorldTasklet
from ypage.nukleon.structs import TaskletControlBlock

if __name__ == '__main__':
    S.startup()
    S.tidIssuer.adjustTID(0)  # 0th Page on 0th Frame
    
    
    print("Yo")
    
    # manual bootstrap here
    hwt = HelloWorldTasklet()
    tcb = TaskletControlBlock(0, 'SYSTEMYA', 'admin', 'support')
    S.registerNewTasklet(tcb)
    S.schedule(tcb, hwt.on_startup)