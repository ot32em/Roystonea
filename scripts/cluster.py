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
        print "cluster#createVMReqHandler"
        values = message.values_of_message(msg)

        # ask algorithm
        print "start ask algorithm"
        addr = self.algorithm_addr
        select_rack_msg = self.create_message(message.AlgorithmSelectRackReq, values)
        rack_addr = self.send_message(addr, select_rack_msg)
        print "end ask algorithm"

        # tell rack to create vm
        print "start send create vm"
        create_vm_msg = self.create_message(message.RackCreateVMReq, values)
        self.send_message(rack_addr, create_vm_msg, context=msg)
        print "end send create vm"

    def createVMResHandler(self, msg, client_address=None):
        print "cluster#createVMResHandler"
        context = self.pop_context(msg)

        if context.request_id == False:
            return

        address = context.caller_address
        res_msg = self.create_message(message.ClusterCreateVMRes, [msg.vmid, msg.status], context)
        self.send_message(address, res_msg)

def start(port, algo_addr):
    server = Cluster("127.0.0.1", port)
    server.algorithm_addr = algo_addr
    server.run()
