from include.base_server import BaseServer

class Algorithm(BaseServer):

    level = "algorithm"

    def __init__(self, host, port):
        super(Algorithm, self).__init__(host, port)

        self.node_addr = None
        self.rack_addr = None
        self.cluster_addr = None

    def register_handle_functions(self):
        self.register_handle_function("AlgorithmSelectClusterReq", self.selectClusterHandler)
        self.register_handle_function("AlgorithmSelectRackReq", self.selectRackHandler)
        self.register_handle_function("AlgorithmSelectNodeReq", self.selectNodeHandler)

    def selectClusterHandler(self, msg, client_address=None):
        return self.cluster_addr

    def selectRackHandler(self, msg, client_address=None):
        return self.rack_addr

    def selectNodeHandler(self, msg, client_address=None):
        return self.node_addr

def start(port):
    server = Algorithm("127.0.0.1", port)
    server.run()
