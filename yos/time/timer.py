class Timer(object):
    """
    A proxy that represents a scheduled execution of a callback
    """
    
    @staticmethod
    def schedule(run_in: float, callback: callable):
        """
        Schedules callback to run in run_in seconds.
        Returns a timer proxy that can be used to cancel it.
        
        Consult your implementation to determine how reliable this is,
        what granularities of run_in you can pass, and what jitter 
        or delay can you expect
        
        Using this means implicitly hinting that ACCURACY counts
        
        @return: Timer instance
        """
        
    @staticmethod
    def repeat(interval: float, callback: callable):
        """
        Schedules callback to run each interval seconds.
        Returns a timer proxy that can be used to cancel it.
        
        Consult your implementation to determine how reliable this is,
        what granularities of run_in you can pass, and what jitter 
        or delay can you expect
        
        Using this means implicitly hinting that REPEATABILITY counts
        
        @return: Timer instance
        """

    def cancel(self):
        """
        Cancels planned execution of this callback
        """