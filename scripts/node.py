from include.base_server import BaseServer
from include import client
from include import message

class Node(BaseServer):

    level = "node"

    def __init__(self, host, port):
        super(Node, self).__init__(host, port)

    def register_handle_functions(self):
        self.register_handle_function("NodeCreateVMReq", self.createVMReqHandler)

    def createVMReqHandler(self, msg, client_address=None):
        status = "ok"
        res_msg = self.create_message(message.NodeCreateVMRes, [msg.vmid, status], context=msg)
        self.send_message(msg.caller_address, res_msg)



