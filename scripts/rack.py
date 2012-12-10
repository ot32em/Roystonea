from include.base_server import BaseServer
from include import message

class Rack(BaseServer):

    level = "rack"

    def __init__(self, host, port):
        super(Rack, self).__init__(host, port)

        self.algorithm_addr = None 

    def register_handle_functions(self):
        self.register_handle_function("RackCreateVMReq", self.createVMReqHandler)
        self.register_handle_function("NodeCreateVMRes", self.createVMResHandler)

    def selectNodeList(self, vm_attr):
        addr = self.algorithm_addr
        msg_values = vm_attr + [ self.addr() ]
        nodeListReq = self.create_message(message.AlgorithmSelectNodeListReq, msg_values )
        return self.send_message( addr, nodeListReq )
<<<<<<< HEAD
=======

    def askAlgorithmName(self):
        req = self.create_message( message.AlgorithmAskNameReq , [] )
        res = self.send_message( self.algorithm_addr, req )
        print("in rack askAlgorithmName method, dump res")
        print( res )
        return res
>>>>>>> 19ec7390d48240103afe4473a8cca46e534fdd70

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
<<<<<<< HEAD

=======
>>>>>>> 19ec7390d48240103afe4473a8cca46e534fdd70
