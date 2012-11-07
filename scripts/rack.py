from include.base_server import BaseServer
from include import client
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
        values = message.values_of_message(msg) + [self.addr()]

        # ask algorithm
        addr = self.algorithm_addr
        node_addr = client.send_message(addr, message.AlgorithmSelectNodeReq(*values))

        # tell node to create vm
        client.sendonly_message(node_addr, message.NodeCreateVMReq(*values))

    def createVMResHandler(self, msg, client_address=None):
        pass
