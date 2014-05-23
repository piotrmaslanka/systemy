from threading import Lock

class NewTIDIssuer(object):
    

    def adjustTID(self, delta: int):
        """
        Increases TID by given value
        """
        with self.lock:
            self.startingTID += delta
    
    def __init__(self):
        self.startingTID = 1    
        self.lock = Lock()

    def next(self) -> int:
        with self.lock:
            tid = self.startingTID
            self.startingTID = tid+1
            return tid