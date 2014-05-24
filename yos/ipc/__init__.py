class SynchronousMessage(object):
   """
   Object passed to a Tasklet when it's called with a
   synchronous message.
   """
   
   def get(self) -> object:
       """Returns the content that's in this message"""
       
       
    def reply(self, obj: object):
        """Issues a reply on this message. This concludes
        the cycle""" 