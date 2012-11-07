from include.base_server import BaseServer

class Node(BaseServer):

    level = "node"

    def __init__(self, host, port):
        super(Node, self).__init__(host, port)

    def register_handle_functions(self):
        self.register_handle_function("NodeCreateVMReq", self.createVMReqHandler)

    def createVMReqHandler(self, message, client_address=None):
        pass

