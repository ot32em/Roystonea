## {{{ http://code.activestate.com/recipes/574454/ (r2)
from SocketServer import ThreadingMixIn, TCPServer
from Queue import Queue
import threading, socket
from thread_base_mix_in import ThreadBaseMixIn

class ThreadPoolMixIn(ThreadingMixIn, ThreadBaseMixIn):
    '''
    use a thread pool instead of a new thread on every request
    '''
    #can be override
    numThreads = 4
    allow_reuse_address = True  # seems to fix socket.error on server restart
    shutdown_event = None
    # __shutdown_signal = False # Whats this ???

    def serve_forever(self):
        '''
        Handle one request at a time until doomsday.
        '''
        # set up the threadpool
        self.requests       = Queue()

        # Handler Thread
        for x in range(self.numThreads):
            self.start_thread(target = self.process_request_thread)

        # Main Thread
        self.threads.append(threading.current_thread())
        
        # Collector Thread
        self.start_thread(target = self.collect_requests)

        # create event for waiting shutdown request to trigger shutdown_event.set()
        self.shutdown_event = threading.Event()
        self.shutdown_event.wait()
        self.server_close()
    
    def shutdown(self):
        while self.shutdown_event == None: pass
        self.shutdown_event.set()

    
    def collect_requests(self):
        while True:
            self.handle_request() # collect every requests incomming and put it in queue
                                  # then, let thread in pool to pick them up to handle


    def process_request_thread(self):
        '''
        obtain request from queue instead of directly from server socket
        '''
        import sys
        while True: 
            request = self.requests.get()
            sys.stderr.write("process request")
            ThreadingMixIn.process_request_thread( self, *request )
    
    def handle_request(self):
        import sys
        sys.stderr.write(".")

        '''
        simply collect requests and put them on the queue for the workers.
        '''
        try:
            sys.stderr.write("before get_request()\n")
            request, client_address = self.get_request()
            sys.stderr.write("after get_request()\n")
        except socket.error:
            return
        if self.verify_request(request, client_address):
            sys.stderr.write("new request from client addr: ")
            sys.stderr.write("%d" % (client_address[1]))
            self.requests.put((request, client_address))

## end of http://code.activestate.com/recipes/574454/ }}}

class ThreadPoolTCPServer (ThreadPoolMixIn, TCPServer):
    pass
