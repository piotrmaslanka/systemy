"""y Development Runtime Profile"""

from ydrp.yeep import yEEP
from ydrp.ynep import yNEP

if __name__ == '__main__':
    # Manually start Support Element
    from ydrp.sysrt import TaskletControlBlock
    from ydrp.support import SupportElementTasklet
    from ydrp import globals
    st = SupportElementTasklet()
    tcb = TaskletControlBlock(0, 'admin', 'SupportElement', 'SYSTEMYA')
    
    globals.SysRTI.tcbs[0] = tcb
    globals.SysRTI.tasklets[0] = st
    globals.yEEP.put(tcb, st.on_startup)
    
    print("YDRP: SupportElement tasklet (TID=0 SYSTEMYA.admin.SupportElement) started")
    
    globals.yEEP.start()
    globals.yNEP.start()