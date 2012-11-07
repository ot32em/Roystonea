from Roystonea.scripts.rack import Rack
from Roystonea.scripts.node import Node
from Roystonea.scripts.algorithm import Algorithm
from Roystonea.scripts.include import message
from Roystonea.scripts.include import client
from support import message_factory
from mock import MagicMock, ANY
import threading
import random
from time import sleep

HOST = "127.0.0.1"
PORT = random.randrange(20000, 30000)

def test_rack():
    message = message_factory.create("RackCreateVMReq")

    # server_stack
    algo_server = Algorithm(HOST, PORT + 2000)
    node_server = Node(HOST, PORT + 1000)
    rack_server = Rack(HOST, PORT)

    # algo setting
    algo_server.node_addr = node_server.addr()

    # rack setting
    rack_server.algorithm_addr = algo_server.addr()

    # node setting
    rack_server.createVMResHandler = MagicMock(return_value="hello world")

    server_stack = [algo_server, node_server, rack_server]

    for server in server_stack:
        def server_thread():
            server.run()

        t = threading.Thread(target = server_thread)
        t.start()

    # client
    try:
        sleep(3)
        client.sendonly_message((HOST, PORT), message)

    finally:
        for server in reversed(server_stack):
            server.shutdown()

    rack_server.createVMResHandler.assert_called_with(ANY, (HOST, ANY))
