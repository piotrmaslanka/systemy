"""Synchronous Message Processor"""
import threading, queue
from ypage.nukleon.structs import TaskletControlBlock
from ypage.nukleon import S
from ypage.interfaces import Processor

class SMP(threading.Thread, Processor):
    def __init__(self):
        threading.Thread.__init__(self)
        
        self.terminated = False
        
    def terminate(self):
        self.terminated = True
        
        
    def run(self):
        while not self.terminated:
            pass