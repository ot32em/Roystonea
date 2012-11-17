from support import server_manager as st
from Roystonea.scripts.cluster import Cluster
from Roystonea.scripts.rack import Rack
from Roystonea.scripts.algorithm import Algorithm
from Roystonea.scripts.monitor import Monitor
from Roystonea.scripts.include.hierachy import *


def test_rack_select_node_list():
    host = st.LOCALHOST
    port = st.get_port()

    alg = Algorithm( host, port)
    monitor = Monitor( host, port+1)
    cluster = Cluster( host, port+14)
    ss = [ alg, monitor, cluster ]

    alg.monitor_addr = monitor.addr()
    cluster.algorithm_addr = alg.addr()

    test_hierachy = Hierachy()
    node1 = NodeDaemonUnit( "node1", host, port+4, "roystonea01")
    node2 = NodeDaemonUnit( "node2", host, port+5, "roystonea02")
    node3 = NodeDaemonUnit( "node3", host, port+6, "roystonea03")
    node4 = NodeDaemonUnit( "node4", host, port+7, "roystonea04")
    node5 = NodeDaemonUnit( "node5", host, port+8, "roystonea05")
    node6 = NodeDaemonUnit( "node6", host, port+9, "roystonea06")
    node7 = NodeDaemonUnit( "node7", host, port+10, "roystonea07")

    rack1 = TreeDaemonUnit( "Rack", "rack1", host, port+11 )
    rack1.addChild(node1)
    rack1.addChild(node2)
    rack1.addChild(node3)
    rack2 = TreeDaemonUnit( "Rack", "rack2", host, port+12 )
    rack2.addChild(node4)
    rack2.addChild(node5)
    rack2.addChild(node6)
    rack3 = TreeDaemonUnit( "Rack", "rack3", host, port+13 )
    rack3.addChild(node7)
    
    cluster1 = TreeDaemonUnit( "Cluster", "cluster1", host, port+14 )
    cluster1.addChild(rack1)
    cluster1.addChild(rack2)
    cluster1.addChild(rack3)


    ds = [node1, node2, node3, node4, node5, node6, node7, rack1, rack2, rack3, cluster1]
    for d in ds :
        test_hierachy.add_daemon( d)


    ''' put test data of resource '''

    node1.set_memory(2)
    node1.set_disk(100)
    node2.set_memory(10)
    node2.set_disk(100)
    node3.set_memory(10)
    node3.set_disk(100)
    node4.set_memory(10)
    node4.set_disk(100)
    # rack1.memory will be 32GB but can fit vm with memory over 10GB
    # rack1.disk will be 400GB but can fit vm with disk over 100GB

    node5.set_memory(26)
    node5.set_disk(150)
    node6.set_memory(2)
    node6.set_disk(200)
    # rack2.memory will be 28 GB
    # rack2.disk will be 350GB

    node7.set_memory(25)
    node7.set_disk(310)
    # rack3.memory will be 25GB
    # rack3.disk will be 310GB


    monitor.hierachy = test_hierachy

    ''' put test data of vm_attributes '''

    vm_attr = [1,1,1,"ubuntu",2,24,300,192,1] # memory 1024, disk 20


    ''' server start '''
    st.start_server_stack( ss, hint=True, sleeptime=4)

    ''' run test method '''
    rack_list = cluster.selectRackList( vm_attr )

    print("returned node_addr_list: "),
    print(rack_list)

    ''' server down '''
    st.shutdown_server_stack( ss )

    expect_list = [ rack3.addr() ]

    assert rack_list == expect_list 

