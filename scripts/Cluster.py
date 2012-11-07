from include.base_server import BaseServer
from include import client
from include import message

class Cluster(BaseServer):

    level = "cluster"

    def __init__(self, host, port):
        super(Cluster, self).__init__(host, port)

        self.algorithm_addr = None 

    def register_handle_functions(self):
        self.register_handle_function("ClusterCreateVMReq", self.createVMReqHandler)
        self.register_handle_function("RackCreateVMRes", self.createVMResHandler)

    def createVMReqHandler(self, msg, client_address=None):
        values = message.values_of_message(msg) + [self.addr()]

        # ask algorithm
        addr = self.algorithm_addr
        rack_addr = client.send_message(addr, message.AlgorithmSelectRackReq(*values))

        # tell rack to create vm
        client.sendonly_message(rack_addr, message.RackCreateVMReq(*values))

    def createVMResHandler(self, msg, client_address=None):
        pass
