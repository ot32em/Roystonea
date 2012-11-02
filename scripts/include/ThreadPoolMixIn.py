## {{{ http://code.activestate.com/recipes/574454/ (r2)
from SocketServer import ThreadingMixIn, TCPServer
from Queue import Queue
import threading, socket


class ThreadPoolMixIn(ThreadingMixIn):
    '''
    use a thread pool instead of a new thread on every request
    '''
    #can be override
    numThreads = 4
    allow_reuse_address = True  # seems to fix socket.error on server restart
    # __shutdown_signal = False # Whats this ???

    def start_thread(self, **kwargs):
        if self.threads == None: self.threads = list()

        t = threading.Thread(target = kwargs['target'])
        t.setDaemon(True)
        t.start()
        self.threads.append(t)

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

        # Wait for die signal Thread
        self.start_thread(target = self.wait_die_by_int )

        # create event for waiting shutdown request to trigger shutdown_event.set()
        self.shutdown_event = threading.Event()
        self.shutdown_event.wait()
        self.server_close()
    
    def wait_die_by_int(self):
        print("Server is waitting your exit signal by typing 'exit', 'bye', or 'shutdown' " )
        while True :
            cmd = raw_input('>') 
            if cmd.lower() in ( 'shutdown', 'exit', 'bye', 'stop' )  :
                self.shutdown_event.set()

    
    def collect_requests(self):
        while True:
            self.handle_request() # collect every requests incomming and put it in queue
                                  # then, let thread in pool to pick them up to handle


    def process_request_thread(self):
        '''
        obtain request from queue instead of directly from server socket
        '''
        while True: 
            ThreadingMixIn.process_request_thread( self, *self.get_request() )
    
    def handle_request(self):
        '''
        simply collect requests and put them on the queue for the workers.
        '''
        try:
            request, client_address = self.get_request()
        except socket.error:
            return
        if self.verify_request(request, client_address):
            self.requests.put((request, client_address))

## end of http://code.activestate.com/recipes/574454/ }}}

class ThreadPoolTCPServer (ThreadPoolMixIn, TCPServer):
    pass
