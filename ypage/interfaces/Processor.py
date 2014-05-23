class Processor(object):
    
    def onTaskletTerminated(self, tcb):
        """
        Called when tasklet with particular TCB was terminated.
        
        Processor should at this point clear everything that belonged
        to that TCB"""