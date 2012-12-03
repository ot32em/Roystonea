from include.base_server import BaseServer
from include import client
from include import message
from vm_manager.vm_ubuntu_manager import VMUbuntuManager

class Node(BaseServer):

    level = "node"

    def __init__(self, host, port):
        super(Node, self).__init__(host, port)

    def register_handle_functions(self):
        self.register_handle_function("NodeCreateVMReq", self.createVMReqHandler)

    def createVMReqHandler(self, msg, client_address=None):
        self.createVM(msg)

        status = "ok"
        res_msg = self.create_message(message.NodeCreateVMRes, [msg.vmid, status], context=msg)
        self.send_message(msg.caller_address, res_msg)

    def createVM(self, msg):
        if msg.vmtype == "ubuntu":
            owner = str(msg.ownerid) # TODO
            hostmachine = "ignore now" # TODO
            vm_manager = VMUbuntuManager(msg.vmid, 
                    owner, 
                    msg.groupid, 
                    msg.vmsubid, 
                    msg.config_memory, 
                    msg.config_disk, 
                    msg.config_cpu, 
                    hostmachine)
        vm_manager.start()


def start(port):
    server = Node("127.0.0.1", port)
    server.run()
