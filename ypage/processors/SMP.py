"""Synchronous Message Processor"""
import threading, queue
from ypage.nukleon.structs import TaskletControlBlock
from yos.tasklets import Tasklet
from ypage.nukleon import S
from ypage.nukleon.NewIDIssuer import NewIDIssuer
from ypage.apipatchers.ipcSynchronousMessage import SynchronousMessageHandler as SynchronousMessage
from ypage.interfaces import Processor
from collections import defaultdict
import itertools

class SMP(threading.Thread, Processor):
    def __init__(self, coreno):
        threading.Thread.__init__(self)
        
        self.terminated = False
        
        self.metalock = threading.RLock()
        
        self.messages = {}      # UUID => (TID waiting for reply, callback)
        self.uuids_by_tid = defaultdict(lambda: [])  # TID waiting for reply => UUIDs waited for
        self.rev_uuids_by_tid = defaultdict(lambda: [])  # TIDs that are supposed to reply => UUIDs waited for
        self.pending_terminations = queue.Queue() # queue of tcbs
        
        self.uuidgen = NewIDIssuer()
        self.uuidgen.adjustID(coreno << 32)
        
    def terminate(self):
        self.terminated = True

    def onTaskletTerminated(self, tcb: TaskletControlBlock):
        self.pending_terminations.put(tcb)
    
    def deliver_reply_to(self, remote_tid: int, target_tid: int, obj: object, msg: SynchronousMessage):
        with self.metalock:
            try:
                tid_waiting_for_reply, callback = self.messages[msg.uuid]
                if tid_waiting_for_reply != target_tid: raise KeyError
            except KeyError:
                return      # invalid!
            
            with S.syslock:
                try:
                    tcb = S.tcbs[target_tid]
                except KeyError:
                    return
            
            del self.messages[msg.uuid]
            self.uuids_by_tid[target_tid].remove(msg.uuid)
            if len(self.uuids_by_tid[target_tid]) == 0:
                del self.uuids_by_tid[target_tid]
            self.rev_uuids_by_tid[remote_tid].remove(msg.uuid)
            if len(self.rev_uuids_by_tid[remote_tid]) == 0:
                del self.rev_uuids_by_tid[remote_tid]
                
            tcb.handlers -= 1
            
            S.schedule(tcb, callback, obj)            
    
    def send_sync_to(self, from_tcb: TaskletControlBlock, target_tid: int, obj: object, handler: callable):
        """
        Called from tasklet. Send a sync message from local tasklet to target tasklet
        """
        if not S.isLocal(target_tid):
            raise NotImplementedError("No IPC for now, sorry!")

        smsg = SynchronousMessage(obj, from_tcb.tid, target_tid, self.uuidgen.next())
        
        with S.syslock:
            if target_tid not in S.tcbs:
                S.schedule(from_tcb, handler, Tasklet.DoesNotExist)
            else:
                S.schedule(S.tcbs[target_tid], S.tcb_inst[target_tid].on_message, from_tcb.tid, smsg)
        
        with self.metalock:
            self.messages[smsg.uuid] = (from_tcb.tid, handler)
            self.rev_uuids_by_tid[target_tid].append(smsg.uuid)
            self.uuids_by_tid[from_tcb.tid].append(smsg.uuid)
            
        from_tcb.handlers += 1
    
    def run(self):
        while not self.terminated:
            try:
                tcb_to_terminate = self.pending_terminations.get(True, 5)
            except queue.Empty:
                continue
            
            with self.metalock:
                a = self.rev_uuids_by_tid.pop(tcb_to_terminate.tid)
                b = self.uuids_by_tid.pop(tcb_to_terminate.tid)                
                for uuid in itertools.chain(a, b):
                    del self.messages[uuid]
                
