from ypage.nukleon import S

import ypage.apipatchers    # this fixes yos module imports

from examples.tcpConnExample import NetworkTest
from ypage.nukleon.structs import TaskletControlBlock

if __name__ == '__main__':
    S.startup()
    S.tidIssuer.adjustTID(0)  # 0th Page on 0th Frame

    
    # manual bootstrap here
    hwt = NetworkTest()
    tcb = TaskletControlBlock(0, 'SYSTEMYA', 'admin', 'support')
    S.registerNewTasklet(tcb, hwt)
    S.schedule(tcb, hwt.on_startup)