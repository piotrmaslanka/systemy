from threading import Lock

class NewIDIssuer(object):
    

    def adjustID(self, delta: int):
        """
        Increases ID by given value
        """
        with self.lock:
            self.startingID += delta
    
    def __init__(self):
        self.startingID = 1    
        self.lock = Lock()

    def next(self) -> int:
        with self.lock:
            tid = self.startingID
            self.startingID = tid+1
            return tid