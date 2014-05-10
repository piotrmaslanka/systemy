class BaseTasklet(object):
    '''
    All y/OS tasklets are supposed to inherit from this
    '''

    def __init__(self, *args, **kwargs):
        """
        Tasklet setup. You should only set up variables
        here. Must be idempotent"""


    def on_startup(self):
        '''
        Entry point for a tasklet
        '''
        
        
    def on_message(self, source, message):
        """
        Called on receiving a message via .send()
        @param source TID of the sender
        @param message An object - content of the message
        """