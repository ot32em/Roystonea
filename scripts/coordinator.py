from include.base_server import BaseServer
from include import message

class Coordinator(BaseServer):

    def __init__(self, host, port):
        super(Coordinator, self).__init__(host, port)

        self.algorithm_addr = None 

    def register_handle_functions(self):
        self.register_handle_function("ClusterCreateVMRes", self.createVMResHandler)

    def createVMResHandler(self, msg, client_address=None):
        ''' Get new VM host node ip, and let moniter to check the VM status 

        Currently, just write to db that the vm is ready
        '''

        print msg

    def create_vm(self, params):
        # this is for test, should be fetch from database
        values = ["vmid", "groupid", "vmsubid", "vmtype", 
                "config_cpu", "config_memory", "config_disk", "config_lifetime", 
                "ownerid"]

        # ask algorithm
        addr = self.algorithm_addr
        select_cluster_msg = self.create_message(message.AlgorithmSelectClusterReq, values)
        cluster_addr = self.send_message(addr, select_cluster_msg)

        create_vm_msg = self.create_message(message.ClusterCreateVMReq, values)
        self.send_message(cluster_addr, create_vm_msg, context=None)

def start(port, algo_addr):
    import threading

    server = Coordinator("127.0.0.1", port)
    server.algorithm_addr = ("127.0.0.1", algo_addr)

    def start_server:
        server.run()

    t = threading.Thread(target = start_server)
    t.start()

