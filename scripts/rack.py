from include.base_server import BaseServer
from include import message

class Rack(BaseServer):

    level = "rack"

    def __init__(self, host, port):
        super(Rack, self).__init__(host, port)

        self.algorithm_addr = None 

        self.memory = -1
        self.disk= -1
        self.minimal_memory = -1
        self.minimal_disk = -1

    def register_handle_functions(self):
        self.register_handle_function("RackCreateVMReq", self.createVMReqHandler)
        self.register_handle_function("NodeCreateVMRes", self.createVMResHandler)

    def register_start_functions(self):
        self.register_start_function( self.testAlgorithm )

    def unit():
        return {"host": self.host, "port": self.port,
                "memory": self.memory, "disk": self.disk,
                "minimal_meory": self.minimal_memory, "minimal_disk": minimal_disk }


    def testAlgorithm(self):
        print( "testAlgorithm called!" )
        self.algorithm_addr = ("localhost", 8002)
        # ask node list from algorithm
        vm_attr= [100, 1, 1, "ubuntu", 1, 1 * 1024 * 1024, 40 * 1024 * 1024, 300, 1]
        req = self.create_message( message.AlgorithmSelectNodeListReq, vm_attr)
        print("algorithm_addr"),
        print( self.algorithm_addr )
        aNodeListRes = self.send_message( self.algorithm_addr, req )

        print( aNodeListRes )
        
        

    def createVMReqHandler(self, msg, client_address=None):
        values = message.values_of_message(msg)

        # ask algorithm
        addr = self.algorithm_addr
        select_node_msg = self.create_message(message.AlgorithmSelectNodeReq, values)
        node_addr = self.send_message(addr, select_node_msg)

        # tell node to create vm
        create_vm_msg = self.create_message(message.NodeCreateVMReq, values)
        self.send_message(node_addr, create_vm_msg, context=msg)

    def createVMResHandler(self, msg, client_address=None):
        context = self.pop_context(msg)

        if context.request_id == False:
            return

        address = context.caller_address
        res_msg = self.create_message(message.RackCreateVMRes, [msg.vmid, msg.status], context)
        self.send_message(address, res_msg)

def start(port, algo_addr):
    server = Rack("127.0.0.1", port)
    server.algorithm_addr = algo_addr
    server.run()

if __name__ == "__main__":
    Rack.cmd_start()

