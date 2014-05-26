import threading, queue, time
from ypage.nukleon.structs import TaskletControlBlock
from ypage.nukleon import S
from ypage.interfaces import Processor
from select import select
from collections import defaultdict

class NEP(threading.Thread, Processor):

    def onTaskletTerminated(self, tcb: TaskletControlBlock):
        self.waiting_terminations.put(tcb)
        
    def __init__(self):
        threading.Thread.__init__(self)
        self.socks = []
        self.sockhandlers = {}      # FileNO => (on_connected, on_read, on_closed, on_failed, on_except)
        self.sock_tcbs = {} # FileNO => TCB
        self.handlers = {}  # FileNO => Amount of handlers that this socket provides
        self.tid_to_sock = defaultdict(lambda: list())
        self.sock_meta_lock = threading.RLock()
        self.waiting_terminations = queue.Queue()
        self.terminated = False

    def terminate(self):
        self.terminated = True
        
    def addSock(self, socket, on_connected, on_read, on_closed, on_failed, on_except):
        """Adds a socket. Called by a foreign thread"""
        
        handlers = 0
        if on_connected != None: handlers += 1
        if on_read != None: handlers += 1
        if on_closed != None: handlers += 1
        if on_failed != None: handlers += 1
        if on_except != None: handlers += 1
        
        with self.sock_meta_lock:
            if socket.fileno() in self.sockhandlers:
                print("ALREADY CONNECTED!!!!")
                return
            self.socks.append(socket)
            self.sockhandlers[socket.fileno()] = (on_connected, on_read, on_closed, on_failed, on_except)
            self.sock_tcbs[socket.fileno()] = S.loc.tcb
            self.handlers[socket.fileno()] = handlers
            self.tid_to_sock[S.loc.tcb.tid].append(socket) 
            
        if not socket.is_client and not socket.issued_on_connected:
            socket.issued_on_connected = True
            if on_connected != None:
                S.schedule(S.loc.tcb, on_connected, socket)
                
        S.loc.tcb.handlers += handlers
            
    def socket_failed(self, sock):
        """yNEP determined that socket is failed, purge it and tell yEEP"""

        fn = sock.fileno()
        hdlr = self.sockhandlers[fn][3]
        if hdlr != None:
            if self.sock_tcbs[fn].is_alive:
                S.schedule(self.sock_tcbs[fn], hdlr, sock)

        with self.sock_meta_lock:
            tcb = self.sock_tcbs[fn]
            del self.sock_tcbs[fn]
            del self.sockhandlers[fn]
            tcb.refsSub(self.handlers[fn])
            del self.handlers[fn]
            self.socks.remove(sock)
            self.tid_to_sock[tcb.tid].remove(sock)
            if len(self.tid_to_sock[tcb.tid]) == 0:
                del self.tid_to_sock[tcb.tid]
                
    def socket_closed(self, sock):    
        """yNEP determined that socket is closed, purge it and tell yEEP"""

        fn = sock.fileno()
        hdlr = self.sockhandlers[fn][2]
        if hdlr != None:
            if self.sock_tcbs[fn].is_alive:
                S.schedule(self.sock_tcbs[fn], hdlr, sock)

        with self.sock_meta_lock:
            tcb = self.sock_tcbs[fn]
            del self.sock_tcbs[fn]
            del self.sockhandlers[fn]
            self.socks.remove(sock)
            tcb.handlers -= self.handlers[fn]
            del self.handlers[fn]            
            self.tid_to_sock[tcb.tid].remove(sock)
            if len(self.tid_to_sock[tcb.tid]) == 0:
                del self.tid_to_sock[tcb.tid]
            
    def iter(self):
        # Prepare socket listing
        with self.sock_meta_lock:
            
            # terminate pending
            while self.waiting_terminations.qsize() > 0:
                tcb = self.waiting_terminations.get()
                for sock in list(self.tid_to_sock[tcb.tid]):  # we need a copy of the list
                    try:
                        sock.close()
                    except OSError:
                        pass
                    self.sock_closed(sock)
                del self.tid_to_sock[tcb.tid]
                
        #    print ("IPv6 GOD: I got", len(self.socks), "in my back pocket") 
            
            for sock in self.socks:
                if sock.is_failed:
                    self.socket_failed(sock)
                    return
                    
            readables = self.socks
            writables = [sock for sock in self.socks if len(sock.writebuf) > 0 or not sock.is_connected]
            exceptables = self.socks
        
        
        if len(readables) == len(writables) == len(exceptables) == 0:
            time.sleep(0.01)
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
            data = r.handleRead()
            
            if r.is_closed:
                self.socket_closed(r)
            elif r.is_failed:
                self.socket_failed(r)
            else:
                h = self.sockhandlers[fn][1]
                if h != None:
                    S.schedule(self.sock_tcbs[fn], h, r, data)
            
        for w in wx:
            if not w.is_connected:
                w.is_connected = True
                fn = w.fileno()
                h = self.sockhandlers[fn][0]
                if h != None:
                    S.schedule(self.sock_tcbs[fn], h, w)

            if len(w.writebuf) > 0:
                try:
                    sl = w.socket.send(w.writebuf)
                    del w.writebuf[:sl]   
                except OSError:
                    w.is_failed = True
                    
                if len(w.writebuf) == 0 and w.close_on_all_write:
                    w.socket.close()
                    self.socket_closed(w)
                    
        for e in ex:
            fn = e.fileno()
            h = self.sockhandlers[fn][4]
            if h != None:
                S.schedule(self.sock_tcbs[fn], h, e)                
    
            
    def run(self):
        while not self.terminated:
            self.iter()        