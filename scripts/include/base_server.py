import SocketServer
import pickle
import threading
import message
from time import sleep
from thread_pool_mix_in import ThreadPoolTCPServer

class BaseServer:
    ''' Base Class for RPC

    Class variable:
        level: specify the type of server
            prototype, node, rack, cluster

    Usage:
        rpc = BaseServer()
        rpc.register_handle_function(name1, function_obj1)
        rpc.register_handle_function(name2, function_obj2)
        rpc.run()
        rpc.shutdown()

    '''

    level = 'prototype'
    shutdown_timeout = 5

    def __init__(self, host, port):
        self.host = host
        self.port = int(port)
        self.handle_functions = {}
        self.server = None
        self.living_threads = {}

    def addr(self):
        ''' Get address: (host, port) '''
        return (self.host, int(self.port))

    def run(self):
        self.server = ThreadPoolTCPServer(self.addr(), self.createHandlerClass())
        self.server.serve_forever()

    def shutdown(self):
        ''' Shutdown after all thread finish or timeout

        Override the shutdown method from ThreadPoolMixIn

        '''
        timer = 0
        isTimeout = False
        while self.number_of_living_threads() > 0 :
            sleep(1)
            timer += 1
            if timer > self.shutdown_timeout :
                isTimeout = True
                break
            print("There still are %d threads not completed. Seconds remaining/timeout: (%d/%d) secs " %
                    ( self.number_of_living_threads(), self.shutdown_timeout, self.shutdown_timeout-timer))
            for t in self.living_threads.values() :
                print("    Thread: %s" % t.name )
        print("Shutting Down! is Timeout: %s" % isTimeout)

        while self.server == None: pass # for server not start yet
        self.server.shutdown()

    def createHandlerClass(self):
        ''' Create HandlerClass for handle request '''

        class BaseServerHandler(SocketServer.BaseRequestHandler):
            ''' This is the inner class for fit the SocketServer.BaseRequestHandler pattern '''

            def handle(self):
                ''' Handle function for TCPServer 

                This function will do the following three steps:

                    1 Collect all the data sended from client, 
                    2 unpack it, 
                    3 perform the correct function

                While handle the request, it will record current thread,
                    * This is for not to interrupt the execution

                '''
                self.master.living_threads[self.request] = threading.current_thread()

                data = self._recv_data()
                self._unpack_and_execute(data)

                del self.master.living_threads[self.request]

            def _recv_data(self):
                data = ""
                while True:
                    raw = self.request.recv(1024)
                    if not raw: break
                    data += raw

                return data
            
            def _unpack_and_execute(self, data):
                message_name = "Undefined"
                try: # try statement for converting serialized data to object-structure data
                    message_name, ret = self.master.unpack_and_execute(data)
                    self.request.send(pickle.dumps(ret))
                
                except pickle.UnpicklingError:
                    error_req = message.Error(msg='Unregonized Serial Data. Can not unpick it. Data Length: %d' % len(data) )
                    self.request.send(pickle.dumps( error_req ) )

                except KeyError:
                    error_req = message.Error(msg='Unacceptable Request Name(Not in DispatchDict). Request Name %s' % message_name )
                    self.request.send(pickle.dumps( error_req ) )


        BaseServerHandler.master = self # let handler access master

        return BaseServerHandler

    def unpack_and_execute(self, data):
        ''' Use pickle.loads to unpack the data and send to registered handle function '''
        recvobj = pickle.loads(data)

        t = threading.current_thread()
        ''' During processing the request,
            it append current request information to threading name, 
            then reset threading name after finish request '''
        short_name = t.name
        recvobj_class_name = recvobj.__class__.__name__
        t.name = short_name+" handling {request_type}".format(request_type = recvobj_class_name)
        return recvobj_class_name, self.handle_functions[recvobj_class_name](recvobj)  # processing request using functions binding in $dispatch_handlers

    def register_handle_function(self, name, function):
        '''
        
        Usage:
        
          def helloworld():
              print("helloworld")
        
          rpcbase.register_handler_function("CmdTest", helloworld)
        '''
    
        self.handle_functions[name] = function

    def unregister_handle_function(self, name):
        '''
        Usage:
        
          rpcbase.unregister_handler_function("CmdTest")
        '''

        self.handle_functions.pop(name)

    def number_of_living_threads(self):
        return len(self.living_threads)

