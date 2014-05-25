from yos.tasklets import Tasklet, Profile
from yos.rt import BaseTasklet

"""
Story is as follows.

A parent creates a child on startup, and can delegate him problems.

Child, upon receiving a problem, creates a delegate to solve that problem for him.
Child sends the problem to delegate, and forwards the answer to the parent
"""

class ParentTasklet(BaseTasklet):
    def on_startup(self):
        Tasklet.start(ChildTasklet, 'childTasklet', None, None, self.on_child_started)
    
    def on_child_started(self, child):
        child.send_sync(4, lambda response: self.on_math_problem_solved('4x4', response))
        child.send_sync(8, lambda response: self.on_math_problem_solved('8x8', response))
        child.send_sync(16, lambda response: self.on_math_problem_solved('16x16', response))
    
    def on_math_problem_solved(self, problem, response):
        print("Child solved problem", problem, "=", response)
    
class ChildTasklet(BaseTasklet):
    def on_message(self, source, syncMsg):
        Tasklet.start(ChildDelegateTasklet, 'childDelegate', None, None, 
                        lambda child: self.on_delegate_started(syncMsg, child))
        
    def on_delegate_started(self, syncMsg, delegate):
        delegate.send_sync(syncMsg.get(), lambda response: syncMsg.reply(response))
        
        
class ChildDelegateTasklet(BaseTasklet):
    def on_message(self, source, syncMsg):
        val = syncMsg.get()
        val = val * val
        syncMsg.reply(val)
