from include.base_server import BaseServer
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
        values = message.values_of_message(msg)

        # ask algorithm
        addr = self.algorithm_addr
        select_rack_msg = self.create_message(message.AlgorithmSelectRackReq, values)
        rack_addr = self.send_message(addr, select_rack_msg)

        # tell rack to create vm
        create_vm_msg = self.create_message(message.RackCreateVMReq, values)
        self.send_message(rack_addr, create_vm_msg, context=msg)

    def createVMResHandler(self, msg, client_address=None):
        context = self.pop_context(msg)

        if context.request_id == False:
            return

        address = context.caller_address
        res_msg = self.create_message(message.ClusterCreateVMRes, [msg.vmid, msg.status], context)
        self.send_message(address, res_msg)
