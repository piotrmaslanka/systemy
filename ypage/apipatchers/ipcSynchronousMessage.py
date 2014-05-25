from yos.ipc import SynchronousMessage
from ypage.nukleon import S

class SynchronousMessageHandler(SynchronousMessage):
    
    def __init__(self, content, senderTid: int, targetTid: int, uuid):
        self.content = content
        self.uuid = uuid
        self.sender = senderTid
        self.target = targetTid
    
    def get(self) -> object:
        return self.content
       
    def reply(self, obj: object):
        S.getSMP(self.sender).deliver_reply_to(self.target, self.sender, obj, self)        

# RIGHT NOW THIS DOES NOT REQUIRE ANY PATCHING
#import yos.ipc
#yos.ipc.SynchronousMessage = SynchronousMessageHandler