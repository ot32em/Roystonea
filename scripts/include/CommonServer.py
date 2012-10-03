#{{{ http://code.activestate.com/recipes/574454/ (r2)
from SocketServer import  TCPServer, BaseRequestHandler
import pickle
from Queue import Queue
import threading, socket
from threading import Event
from time import sleep
from scripts.include import Message
from scripts.include.PM import *

class CommonServer(TCPServer):
    '''
    use a thread pool instead of a new thread on every request
    '''
#    num_rthreads = 4  
    allow_reuse_address = True  # seems to fix socket.error on server restart

    def __init__(self, addr, level, num_rthreads, dispatch_handlers, startup_functions):
    # inherit TCPServer to init SocketServer-based critical variable
    # binding dispatch_handlers, startup functions from parameter 
    # create threads record and request pool(queue).
        listening_addr = ('', addr[1] )
        TCPServer.__init__(self, addr, RequestDispatchHandler)

        self.level = level
        self.addr = addr
        self.num_rthreads = num_rthreads # How many threads who handle the requests
        self.dispatch_handlers = dispatch_handlers # a dictionary with { 'Message Name': Binding Function, ... }
        self.startup_functions = startup_functions # a list with { Binding Function, ... }
        self.pm_relation = PM_Entry().setAll( level=level, addr = addr )
    
        self.threads = list() # record the threads we use
        self.requests = Queue(self.num_rthreads) # init the requests pool as queue type

    def serve_forever(self, console_off=False):
    # Main Running Function 
    #   a.init server varable
    #   b.assign main jobs to each threads
    #     Job 1 : Collect requests to pool
    #     Job 2 : Process requests from pool
    #     Job 3 : Command shell
    #     Job 4 : Startup functions
    # == wait shutdown signal ===
    #   c.shutdown procedure


        ''' Init Shutdown Signal Variables'''
        self.numProcessingRequestThreads = 0 # increse when a thread start to handle the request, and decrease it when complete.
        self.livingThreads = dict()
        self.shutdown_timeout = 5 # wait secs to let thread complete its job or terminal it.
        self.__is_thread_call_shutdown = Event() # let main thread in serve_forever() know when init the shutdown procedure


        ''' Assigning Jobs to Each threads '''
        self.assignThreadJob( method=self.collectRequests, name="Thread of Collecting Requests Into Pool")

        for x in range(self.num_rthreads):
            self.assignThreadJob( method=self.processPoolRequests, name="No.%d Thread of Processing Pool Requests" % (x+1))
        
        for func in self.startup_functions:
            self.assignThreadJob( method=func , name="Thread of Startup Function ['%s']" % ( func.__name__) ) 
       
        if not console_off:
            self.assignThreadJob( method=self.waitCmd, name="Thread of cmd shell")
       
        ''' Wait Shutdown Signal'''
        # Main thread blocked here to keep server running until some thread call shutdown
        self.__is_thread_call_shutdown.wait()
        
        ''' Shutdown Procedure (Wait threads completed.) '''
        # Check there are living threads every seconds until self.timeout.
        # If no living threads, directly shutdown server, or force to shutdown server after timeout counting
        timer = 0
        isTimeout = False
        while self.numProcessingRequestThreads > 0 :
            sleep(1)
            timer += 1
            if timer > self.shutdown_timeout :
                isTimeout = True
                break
            print("There still are %d threads not completed. Seconds remaining/timeout: (%d/%d) secs " %
                    ( self.numProcessingRequestThreads, self.shutdown_timeout, self.shutdown_timeout-timer))
            for t in self.livingThreads.values() :
                print("    Thread: %s" % t.name )
        print("Shutting Down! is Timeout: %s" % isTimeout)
        self.server_close()

    ''' Thread job methods '''

    def assignThreadJob(self, method, name=""):
    # Wrap thread init procedures including a.init thread, b.set Daemon, c. put thread to record, and d.run it
        t = threading.Thread(target=method, name=name)
        t.setDaemon(True)
        self.threads.append(t)
        t.start()

    def threadCallShutdown(self):
    # Trigger the shutdown signal, notify all threads server is going to shutdown
        self.__is_thread_call_shutdown.set()

    def waitCmd(self):
    # A simple shell that supports shutdown, list threads, ping machine, and show pm relation command.
        print('You can type "?", "help", or "h" to know commands' )
        prompt = ">"
        while True :
            try: 
                cmd = raw_input(prompt)
                if cmd.lower() in ('help','?', 'h') :
                    print( '='*60 )
                    print("exit             => Shutdown Server")
                    print("sdt HOST PORT    => Remotely Shutdown the Server @ HOST:PORT ")
                    print("sdc              => Shutdown All the Children")
                    print("sdtc             => Remotely Shutdown Machine's all children")
                    print("ping HOST PORT   => Send Empty Message to CommonHandler-based Machine to Check Whether Alive")
                    print("ls               => Show Status of All Threads")
                    print("sr               => Show PM Relation")
                    print("str HOST PORT    => Remotely Show The PM Relation @ HOST:PORT")
                    print("sp HOST PORT     => set machine's parent@HOST:PORT")
                    print("ac HOST PORT     => add child to machine")
                    print( '='*60 )

                ''' Shutdown '''
                if cmd.split(' ')[0].lower() in ( 'shutdown', 'sd', 'exit', 'bye', 'stop', )  :
                    chain_shutdown = False
                    if len( cmd.split(' ') ) >= 2 :
                        chain_shutdown = True if cmd.split(' ')[1] in ('chain_shutdown') else False
                    self.cmdShutdown(chain_shutdown)

                ''' Ping Test '''
                if cmd.lower().split(' ')[0] in ( 'ping' ) :
                    argv = cmd.lower().split(' ')
                    if len(argv) <= 2 :
                        print("ping usage: ping HOST PORT")
                        continue

                    self.cmdPing( addr = (argv[1], int( argv[2] ) ) )

                ''' Show Threads Status '''
                if cmd.lower() in ( 'list threads', 'list', 'ls' ) :
                    self.cmdListThreads()

                ''' Show Relation '''
                if cmd.split(' ')[0].lower() in ( 'showrelation', 'sr' ):
                    style = 4
                    if len( cmd.split(' ') ) > 1 :
                        if cmd.split(' ')[1] in ('1','2','3','4') :
                            style = int( cmd.split(' ')[1] )

                    self.cmdShowRelation(style)

                ''' Show The Relation '''
                if cmd.split(' ')[0].lower() in ( 'showtherelation', 'str' ):
                    if len( cmd.split(' ') ) >= 3 :
                        host = cmd.split(' ')[1]
                        port = cmd.split(' ')[2] 
                        if not port.isdigit() :
                            continue
                        port = int(port)
                        addr = (host, port )

                        style = 4
                        if len( cmd.split(' ') ) >= 4 :
                            if cmd.split(' ')[1] in ('1','2','3','4') :
                                style = int( cmd.split(' ')[3] )

                    self.cmdShowTheRelation(addr, style)


                ''' Set Parent '''
                if cmd.lower().split(' ')[0] in ('setparent', 'sp') :
                    host = cmd.split(' ')[1]
                    port = int( cmd.split(' ')[2] )
                    addr = (host, port)
                    self.cmdSetParent( addr )

                ''' Add Child '''
                if cmd.lower().split(' ')[0] in ('addchild', 'ac' ) :
                    host = cmd.split(' ')[1]
                    port = int( cmd.split(' ')[2] )
                    addr = (host, port)
                    self.cmdAddChild( addr )

                ''' Shutdown Children '''
                if cmd.lower() in ('shutdownchildren', 'sdc') :
                    chain_shutdown = False
                    if len( cmd.split(' ') ) >= 2 :
                        chain_shutdown = True if cmd.split(' ')[1] in ('chain_shutdown') else False
                    self.cmdShutdownChildren()

                ''' Shutdown Remote Machine@addr 's children '''
                if cmd.lower().split(' ')[0] in ( 'sdtc', 'shutdownthechildren' ) :
                    if len( cmd.lower().split(' ') ) >= 3 :
                        host = cmd.split(' ')[1]
                        port = int( cmd.split(' ')[2] )
                        addr = (host , port )
                        chain_shutdown = False
                        if len( cmd.split(' ') ) >= 4 :
                            chain_shutdown = True if cmd.split(' ')[3] in ('chain_shutdown') else False
                        
                        self.cmdShutdownTheChildren( addr, chain_shutdown )

                ''' Shutdown One Machine '''
                if cmd.split(' ')[0].lower() in ('shutdownthe', 'sdt' ) :
                    host = cmd.split(' ')[1]
                    port = int( cmd.split(' ')[2] )
                    addr = (host, port )

                    chain_shutdown = False
                    if len( cmd.split(' ') ) >= 4 :
                        chain_shutdown = True if cmd.split(' ')[3] in ('chain_shutdown') else False
                    self.cmdShutdownThe( addr, chain_shutdown )

            except KeyError as e:
                print("in WaitCmd, Unknown Cmd Name, msg: %s" % e )
            
            except Exception as e :
                print( "%s" % e ) 

    def cmdShowRelation(self, style = 4):
        req = Message.CmdGetPMRelationReq( )
        res = self.dispatch_handlers['CmdGetPMRelationReq']( req )
        style = int (style)
        if style == 1 :
            print( res.dump_one_row )
        elif style == 2 :
            print( res.dump_two_rows )
        elif style == 3:
            print( res.dump_children_rows)
        else:
            print( res.dump_pretty )

    def cmdShowTheRelation(self, addr, style = 4):
        req = Message.CmdGetThePMRelationReq(dest_addr = addr )
        res = self.dispatch_handlers['CmdGetThePMRelationReq']( req )
        style = int (style)
        if style == 1 :
            print( res.dump_one_row )
        elif style == 2 :
            print( res.dump_two_rows )
        elif style == 3:
            print( res.dump_children_rows)
        else:
            print( res.dump_pretty )


    def cmdSetParent(self, parent_addr):
        req = Message.CmdSetParentReq(parent_addr = parent_addr)
        res = self.dispatch_handlers['CmdSetParentReq'](req)
        self.cmdShowRelation()

    def cmdAddChild(self, child_addr):
        req = Message.CmdAddChildReq( child_addr = child_addr )
        res = self.dispatch_handlers['CmdAddChildReq'](req)
        self.cmdShowRelation()

    def cmdShutdown(self, chain_shutdown = False ):
        req = Message.CmdShutdownReq( chain_shutdown = chain_shutdown)
        res = self.dispatch_handlers['CmdShutdownReq']( req )


    def cmdShutdownThe(self, addr, chain_shutdown = False):
        req = Message.CmdShutdownTheReq( dest_addr = addr, chain_shutdown = chain_shutdown )
        res = self.dispatch_handlers['CmdShutdownTheReq']( req )

    def cmdShutdownTheChildren(self, addr, chain_shutdown = False) :
        req = Message.CmdShutdownTheChildrenReq(dest_addr = addr, chain_shutdown = chain_shutdown)
        res = self.dispatch_handlers['CmdShutdownTheChildrenReq']( req )
         

    def cmdShutdownChildren(self, chain_shutdown = False):
        req = Message.CmdShutdownChildrenReq(chain_shutdown = chain_shutdown)
        res = self.dispatch_handlers['CmdShutdownChildrenReq']( req )
        
    def cmdPing(self, addr, times=4):
        req = Message.CmdGetPingReq( dest_addr = addr, times = 4)
        cmdres = self.dispatch_handlers['CmdGetPingReq']( req) 
        print(cmdres.msg)

    def cmdListThreads(self):
    # List all threads status in records
        print("numProcessingRequestThreads: %d" % self.numProcessingRequestThreads ) 
        print("__is_thread_call_shutdown isSet: %s" % self.__is_thread_call_shutdown.is_set() ) 
        for t in self.threads :
            print("%s is alive: %s" % ( t.getName(), t.isAlive() ) )
    
    def collectRequests(self):
    # Simply accept incoming requests and put it in pool.
        while True:
            try:
                request, client_address = self.get_request()
            except socket.error:
                return
            if self.verify_request(request, client_address):
                self.requests.put((request, client_address))

    def processPoolRequests(self):
    #  Always pick up request from pool ( wait/block if no request in pool),
    #  unless the EVENT of SHUTDOWN called. and handle it including 
    #  exception error and clean up procedures.
        while True and self.__is_thread_call_shutdown.is_set() == False: 
            # Pick up from pool.
            request, child_address = self.requests.get()
            try:
                # Process it
                self.finish_request( request, child_address )
            except Exception:
                self.handle_error( request, child_address )
            finally:
                self.close_request( request )

    def finish_request(self, request, client_address):
        self.numProcessingRequestThreads += 1
        self.livingThreads[request] = threading.current_thread()

        self.RequestHandlerClass(request, client_address, self, self.dispatch_handlers)

        del self.livingThreads[request]
        self.numProcessingRequestThreads -= 1

class RequestDispatchHandler(BaseRequestHandler):
    def __init__(self, request, client_address, server, dispatch_handlers):
        self.dispatch_handlers = dispatch_handlers
        BaseRequestHandler.__init__(self, request, client_address, server)

    def handle(self):
        ''' Dispatch Every Request to its own Handler by reqDispatchDic[key(reqName)]=value(reqObj) '''
        # Recv Full-length Serial Data
        data = ""
        input = True
        while input:
            input = self.request.recv(4096)
            data += input
        
        try: # try statement for converting serialized data to object-structure data
            recvobj = pickle.loads(data)

            t = threading.current_thread()
            ''' During processing the request,
                it append current request information to threading name, 
                then reset threading name after finish request '''
            short_name = t.name
            t.name = short_name+" handling {request_type}".format(request_type = recvobj.__class__.__name__ )
            ret = self.dispatch_handlers[recvobj.__class__.__name__](recvobj)  # processing request using functions binding in $dispatch_handlers
            t.name = short_name 

            self.request.send(pickle.dumps(ret))
        
        except pickle.UnpicklingError:
            error_req = Message.Error(msg='Unregonized Serial Data. Can not unpick it. Data Length: %d' % len(data) )
            self.request.send(pickle.dumps( error_req ) )

        except KeyError:
            error_req = Message.Error(msg='Unacceptable Request Name(Not in DispatchDict). Request Name %s' % recvobj.__class__.__name__ )
            self.request.send(pickle.dumps( error_req ) )

