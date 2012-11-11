from Roystonea.scripts.coordinator import Coordinator
from Roystonea.scripts.cluster import Cluster
from Roystonea.scripts.rack import Rack
from Roystonea.scripts.node import Node
from Roystonea.scripts.algorithm import Algorithm
from support import server_manager
import random
from time import sleep

HOST = "127.0.0.1"
PORT = random.randrange(20000, 25000)

def test_coordinator():

    # server_stack
    algo_server = Algorithm(HOST, PORT + 4)
    node_server = Node(HOST, PORT + 3)
    rack_server = Rack(HOST, PORT + 2)
    cluster_server = Cluster(HOST, PORT + 1)
    coordinator_server = Coordinator(HOST, PORT)

    # algo setting
    algo_server.node_addr = node_server.addr()
    algo_server.rack_addr = rack_server.addr()
    algo_server.cluster_addr = cluster_server.addr()

    rack_server.algorithm_addr = algo_server.addr()
    cluster_server.algorithm_addr = algo_server.addr()
    coordinator_server.algorithm_addr = algo_server.addr()

    # setup function for assert
    holder = {'createVMResHandler_get_called': False}
    def f(self, message):
        holder['createVMResHandler_get_called'] = True
    coordinator_server.createVMResHandler = f

    # start servers
    server_stack = [algo_server, node_server, rack_server, cluster_server, coordinator_server]
    server_manager.start_server_stack(server_stack)

    try:
        sleep(5)
        coordinator_server.create_vm(None)

        counter = 0
        while counter < 10 and holder['createVMResHandler_get_called'] == False:
            sleep(1)
            counter += 1
    except Exception as e:
        print e

    finally:
        server_manager.shutdown_server_stack(server_stack)

    assert holder["createVMResHandler_get_called"] == True
