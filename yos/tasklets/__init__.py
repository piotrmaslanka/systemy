from yos import YOSException

class Tasklet(object):
    """Class describing a tasklet"""
    
    class DoesNotExist(YOSException):
        """Given tasklet does not exist"""
        
    class AccessDenied(YOSException):
        """Is is not allowed to access this tasklet"""
        
    @staticmethod
    def me():
        """
        Returns Tasklet object that represents the caller.
        Does not block
        @return yos.tasklets.Tasklet representing the caller
        """
        
    @staticmethod
    def start(taskletCls, newname: str='Tasklet', newgroup: str=None, newuser: str=None, result1: str=None, *args, **kwargs):
        """
        Starts a new tasklet with given parameters
        
        @param taskletCls class describing tasklet to launch
        @param newname Name of new tasklet
        @param newgroup Name of new tasklet's group. Pass something else than None
               only if you have privileges to do so, else AccessDenied will be thrown
        @param newuser Name of new tasklet's user. Pass something else than None
               only if you have privileges to do so, else AccessDenied will be thrown
        @param result1 callable/1 to call with yos.tasklets.Tasklet instance on completion
        @param *args arguments to pass to tasklet constructor
        @param **kwargs arguments to pass to tasklet constructor
        @raise Tasklet.AccessDenied: thrown if there's no permission to perform the job 
        """

    @staticmethod
    def open(tid: int, result1: callable):
        """
        Returns an object representing target tasklet
        
        @param tid Tasklet Identifier
        @param result1 callable/1 to call with Tasklet or specific exception class if it fails
                       AccessDenied if tasklet has no privileges to open target
                       DoesNotExist if target tasklet does not exist
        """
        
        # self.tid = tid          #: int
        # self.group = None       #: str
        # self.name = None        #: str
        # self.user = None        #: str
        
        
    def send(self, obj: object, result1: callable=None):
        """
        Sends given tasklet an object without blocking
        
        @param obj Object to send
        @param result1 callable/1 that will be passed a True whether the call succeeded
               of exception class if it doesn't
                       AccessDenied if tasklet has no privileges to open target
                       DoesNotExist if target tasklet does not exist
        """

    @staticmethod
    def send_to(tid: int, obj: object, result1: callable=None):
        """
        Sends an object to a tasklet specified by it's TID
        
        @param tid TID of recipient tasklet
        @param obj Object to send
        @param result1 callable/1 that will be passed a True whether the call succeeded
               of exception class if it doesn't
                       AccessDenied if tasklet has no privileges to open target
                       DoesNotExist if target tasklet does not exist
        """        

class Profile(object):
    """
    Class used to tell runtime about execution profile of current tasklet
    """
    
    @staticmethod
    def disable_gc():
        """
        Disables garbage collection for current tasklet
        """
        
    @staticmethod
    def enable_gc():
        """
        Enable garbage collection for current tasklet
        """        
        
    @staticmethod
    def is_gc_enabled() -> bool:
        """
        Returns whether GC is enabled for current tasklet
        
        @return bool whether GC is enabled for current tasklet
        """