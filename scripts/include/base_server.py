import SocketServer
import pickle
import threading
import message
import client
from time import sleep
from thread_pool_mix_in import ThreadPoolTCPServer
from thread_base_mix_in import ThreadBaseMixIn

class BaseServer(ThreadBaseMixIn, object):
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
        self.start_functions = []
        self.server = None
        self.living_threads = {}
        self.request_count = 1
        self.request_context = {}

    def addr(self):
        ''' Get address: (host, port) '''
        return (self.host, int(self.port))

    def register_handle_functions(self):
        ''' This function should override by child class '''
        pass
    
    def register_start_functions(self):
        ''' This function should override by child class '''
        pass

    def turn_on_start_functions(self):
        if len(self.start_functions) == 0: return

        sleep(3) # wait server start
        for f in self.start_functions:
            self.start_thread(target = f)

    def run(self):
        self.register_handle_functions()
        self.register_start_functions()
        self.start_thread(target = self.turn_on_start_functions)
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
                    ( self.number_of_living_threads(), self.shutdown_timeout-timer, self.shutdown_timeout))
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
                    message_name, ret = self.master.unpack_and_execute(data, self.client_address)
                    self.request.send(pickle.dumps(ret))
                
                except pickle.UnpicklingError:
                    error_req = message.Error(msg='Unregonized Serial Data. Can not unpick it. Data Length: %d' % len(data) )
                    self.request.send(pickle.dumps( error_req ) )

                except KeyError:
                    error_req = message.Error(msg='Unacceptable Request Name(Not in DispatchDict). Request Name %s' % message_name )
                    self.request.send(pickle.dumps( error_req ) )

        BaseServerHandler.master = self # let handler access master

        return BaseServerHandler

    def unpack_and_execute(self, data, client_address=None):
        ''' Use pickle.loads to unpack the data and send to registered handle function '''
        recvobj = pickle.loads(data)

        t = threading.current_thread()
        ''' During processing the request,
            it append current request information to threading name, 
            then reset threading name after finish request '''
        short_name = t.name
        recvobj_class_name = recvobj.__class__.__name__
        t.name = short_name+" handling {request_type}".format(request_type = recvobj_class_name)
        return recvobj_class_name, self.handle_functions[recvobj_class_name](recvobj, client_address)  # processing request using functions binding in $dispatch_handlers

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

        if self.handle_functions.has_key(name):
            self.handle_functions.pop(name)

    def register_start_function(self, function):
        self.start_functions.append(function)

    def number_of_living_threads(self):
        return len(self.living_threads)

    def create_message(self, msg_class, values, context=None):
        _values = values[:]
        if "Req" in msg_class.__name__:
            _values += [self.addr(), self.request_count]
        elif "Res" in msg_class.__name__ and context:
            _values += [context.request_id]

        self.request_count+=1

        return msg_class(*_values)

    def send_message(self, address, message, context=None):
        if context:
            self.request_context[message.request_id] = context
            client.sendonly_message(address, message)
        else:
            return client.send_message(address, message)

    def pop_context(self, message):
        return self.request_context.pop(message.request_id)

    @classmethod
    def cmd_start(cls):
        try:
            import sys
            import threading
            host = sys.argv[1]
            port = int( sys.argv[2] )
            server = cls(host, port )
            def server_start():
                server.run()
            t = threading.Thread( target = server_start )
            t.start()
            while 1:
                input = raw_input(": ")
                if input == "":
                    print("commands: ")
                    print("  exit")
                    print("  status")
                if input == "exit" :
                    break;
                if input == "status" :
                    print("level: %s" % server.level)
                    print("shutdown_timeout: %s" % server.shutdown_timeout)
                    print("host: %s" % server.host )
                    print("port: %s" % server.port )

                    print("handle_funtions:")
                    print(server.handle_functions)
                    print("start_functions")
                    print(server.start_functions)
                    print("server")
                    print(server.server)
                    print("living_threads")
                    print(server.living_threads)
            server.shutdown()

        except IndexError as e:
            print("usage: python daemon.py hostname port(int)")
        
