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
        self.pop_context(msg)
