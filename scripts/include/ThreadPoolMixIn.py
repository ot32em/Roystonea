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
    __shutdown_signal = False

    def serve_forever(self):
        '''
        Handle one request at a time until doomsday.
        '''
        # set up the threadpool
        self.threads = list()
        self.requests = Queue(self.numThreads)
        self.shutdown_event=threading.Event()

        for x in range(self.numThreads):
            t = threading.Thread(target = self.process_request_thread)
            t.setDaemon(True)
            t.start()
            self.threads.append(t)
        self.threads.append(threading.current_thread())
        
        # server main loop
        '''while True:
            print("main thread is listening ")
            self.handle_request() # collect every requests incomming and put it in queue
                                  # then, let thread in pool to pick them up to handle
            print("main thread listen recv %s request" % times)
            times += 1 '''
        t = threading.Thread(target = self.collect_requests)
        t.setDaemon(True)
        t.start()
        self.threads.append(t)

        t = threading.Thread(target = self.wait_die_by_int )
        t.setDaemon(True)
        t.start()
        self.threads.append(t)

        
        # create event for waiting shutdown request to trigger shutdown_event.set()
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
            # original version of following code is:
            # ThreadingMixIn.process_request_thread( self, *self.get_request() )
            # because I can not yet understand the wildcard symbol '*' as prefix of self.get_request()
            # and I usually forget what process_request_thread is doing
            # So I write it explicily to let me know what is happening
            request, child_address = self.get_request()
            try:
                self.finish_request( request, child_address )
            except Exception:
                self.handle_error( request, child_address )
            finally:
                self.shutdown_request( request )


    
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
