class BaseTasklet(object):
    '''
    All y/OS tasklets are supposed to inherit from this.
    
    By default, they won't be garbage collected. They will
    need to explicitly enable it
    '''

    def __init__(self, *args, **kwargs):
        """
        Tasklet setup. You should only set up variables
        here. Must be idempotent"""


    def on_startup(self):
        '''
        Entry point for a tasklet
        '''
        
        
    def on_message(self, source: int, message: object):
        """
        Called on receiving an asynchronous message or synchronous message
        
        If it's a synchronous message, it will be an instance of yos.ipc.SynchronousMessage,
        and you should answer it - sooner or later
        
        @param source TID of the sender
        @param message An object - content of the message
        """
        
        
class GCTasklet(BaseTasklet):
    """
    A garbage-collected tasklet. Runtime should recognize
    this inheritance and flag the GC flag
    """