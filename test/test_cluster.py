from Roystonea.scripts.cluster import Cluster
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
PORT = random.randrange(20000, 25000)

def test_cluster():
    message = message_factory.create("ClusterCreateVMReq")

    # server_stack
    algo_server = Algorithm(HOST, PORT + 3000)
    node_server = Node(HOST, PORT + 2000)
    rack_server = Rack(HOST, PORT + 1000)
    cluster_server = Cluster(HOST, PORT)

    # algo setting
    algo_server.node_addr = node_server.addr()
    algo_server.rack_addr = rack_server.addr()

    # cluster setting
    cluster_server.algorithm_addr = algo_server.addr()
    cluster_server.createVMResHandler = MagicMock(return_value="hello world")

    # rack setting
    rack_server.algorithm_addr = algo_server.addr()

    server_stack = [algo_server, node_server, rack_server, cluster_server]

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

    cluster_server.createVMResHandler.assert_called_with(ANY, (HOST, ANY))
