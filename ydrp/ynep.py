import socket
from ydrp import globals
from threading import Thread, RLock
from select import select
import ydrp.sysio
import time

class yNEP(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.socks = []
        self.sockhandlers = {}      # FileNO => (on_connected, on_read, on_closed, on_failed, on_except)
        self.sock_tcbs = {} # FileNO => TCB
        self.sock_meta_lock = RLock()
        self.terminated = False
        
    def terminate(self):
        self.terminated = True
        
    def addSock(self, socket, on_connected, on_read, on_closed, on_failed, on_except):
        """Adds a socket. Called by a foreign thread"""
        with self.sock_meta_lock:
            self.socks.append(socket)
            self.sockhandlers[socket.fileno()] = (on_connected, on_read, on_closed, on_failed, on_except)
            self.sock_tcbs[socket.fileno()] = globals.loc.current_tcb
            
    def socket_failed(self, sock):
        """yNEP determined that socket is failed, purge it and tell yEEP"""

        fn = sock.fileno()
        hdlr = self.sockhandlers[fn][3]
        if hdlr != None:
            globals.yEEP.put(self.sock_tcbs[fn], hndlr, sock)

        with self.sock_meta_lock:
            del self.sock_tcbs[fn]
            del self.sockhandlers[fn]
            self.socks.remove(sock)
        
    def socket_closed(self, sock):    
        """yNEP determined that socket is closed, purge it and tell yEEP"""

        fn = sock.fileno()
        hdlr = self.sockhandlers[fn][2]
        if hdlr != None:
            globals.yEEP.put(self.sock_tcbs[fn], hdlr, sock)

        with self.sock_meta_lock:
            del self.sock_tcbs[fn]
            del self.sockhandlers[fn]
            self.socks.remove(sock)
    
            
    def iter(self):
        # Prepare socket listing
        with self.sock_meta_lock:
            for sock in self.socks:
                if sock.is_failed:
                    self.socket_failed(sock)
                    return
                    
            readables = self.socks
            writables = [sock for sock in self.socks if len(sock.writebuf) > 0 or not sock.is_connected]
            exceptables = self.socks
        
        
        if len(readables) == len(writables) == len(exceptables) == 0:
            time.sleep(0)
            return

        try:
            rx, wx, ex = select(readables, writables, exceptables, 5)
        except OSError as e:
            # Go thru every socket, check if it's failed
            for sock in self.socks:
                try:
                    select((sock, ), (), (), 0)
                except OSError:
                    self.socket_failed(sock)
                    return
            rx, wx, ex = (), (), ()
                
        # Process readables
        for r in rx:
            fn = r.fileno()
            r.handleRead()
            
            if r.is_closed:
                self.socket_closed(r)
            else:
                h = self.sockhandlers[fn][1]
                if h != None:
                    globals.yEEP.put(self.sock_tcbs[fn], h, r)
            
        for w in wx:
            if not w.is_connected:
                w.is_connected = True
                fn = w.fileno()
                h = self.sockhandlers[fn][0]
                if h != None:
                    globals.yEEP.put(self.sock_tcbs[fn], h, w)

            if len(w.writebuf) > 0:
                try:
                    sl = w.socket.send(w.writebuf)
                    del w.writebuf[:sl]   
                except OSError:
                    w.is_failed = True
                    
        for e in ex:
            fn = e.fileno()
            h = self.sockhandlers[fn][4]
            if h != None:
                globals.yEEP.put(self.sock_tcbs[fn], h, e)                
    
            
    def run(self):
        while not self.terminated:
            self.iter()
        
globals.yNEP = yNEP()