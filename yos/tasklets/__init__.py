class Tasklet(object):
    """Class describing a tasklet"""
    
    class DoesNotExist(Exception):
        """Given tasklet does not exist"""
        
    class AccessDenied(Exception):
        """Is is not allowed to access this tasklet"""
        
        
    @staticmethod
    def me():
        """
        Returns Tasklet object that represents the caller.
        Does not block
        @return yos.tasklets.Tasklet representing the caller
        """
        
    @staticmethod
    def start(taskletCls, result1=None, *args, **kwargs):
        """
        Starts a new tasklet with given parameters
        
        @param taskletCls class describing tasklet to launch
        @param result1 callable/1 to call with yos.tasklets.Tasklet instance on completion
        @param *args arguments to pass to tasklet constructor
        @param **kwargs arguments to pass to tasklet constructor
        """

    @staticmethod
    def open(tid, result1):
        """
        Returns an object representing target tasklet
        
        @param tid Tasklet Identifier
        @param result1 callable/1 to call with Tasklet or specific exception class
        """
        
        self.tid = tid          #: int
        self.group = None       #: str
        self.name = None        #: str
        self.user = None        #: str
        
        
    def send(self, obj, result1=None):
        """
        Sends given tasklet an object without blocking
        
        There's no guarantee that it will arrive, as this is asynchronous
        
        @param obj Object to send
        @param result1 callable/1 that will be passed a boolean on whether the call succeeded
        @raise AccessDenied not allowed to send
        """
