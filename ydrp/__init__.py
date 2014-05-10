"""y Development Runtime Profile"""

from ydrp.yeep import yEEP

if __name__ == '__main__':
    # Manually start Support Element
    from ydrp.ysap import TaskletControlBlock
    from ydrp.support import SupportElementTasklet
    from ydrp import globals
    st = SupportElementTasklet()
    tcb = TaskletControlBlock(0, 'YDRPSUPP', 'SupportElement', 'SYSTEMYA')
    
    globals.ySAP.tcbs[0] = tcb
    globals.ySAP.tasklets[0] = st
    globals.yEEP.put(tcb, st.on_startup)
    
    globals.yEEP.start()
    