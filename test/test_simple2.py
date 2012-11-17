from support import server_manager as st # server tool
from Roystonea.scripts.rack import Rack
from Roystonea.scripts.algorithm import Algorithm
from Roystonea.scripts.monitor import Monitor
from time import sleep

def test_rack_get_algorithm_test_data():
    return
    port = st.get_port()
    alg = Algorithm( st.LOCALHOST, port )
    rack = Rack( st.LOCALHOST, port + 1 )
    rack.algorithm_addr = alg.addr()

    ss = [ alg, rack ] # server stack



    # rack.askNodeList send Alg..mAskNodeListReq with no parameters to alg
    # alg.askNodeListHandler use client_addr to know rack_addr
    # setup alg a testData for test rack and algorithm can communicate correctly

    fake_nodelist = [ {"memory": 128, "disk": 40, "host": "roy1", "port": 5001, "hostmachine": "roystonea01" },
                      {"memory": 512, "disk": 120, "host": "roy2", "port": 5002, "hostmachine": "roystonea02" },
                      {"memory": 308, "disk": 800, "host": "roy3", "port": 5003, "hostmachine": "roystonea03" } ]
    print("dump fake_nodelist"),
    print( fake_nodelist )
    def dummySelectNodeHandler(self, msg, client_addr=None):
        return fake_nodelist[:]
    alg.selectNodeListHandler = dummySelectNodeHandler

    st.start_server_stack( ss, True )
    sleep( 4 )

    nodelist = rack.selectNodeList([1,2,3,4,5,6,7,8,9])
    print(" dump returned nodelist: "),
    print(nodelist)
    assert nodelist == fake_nodelist
    

    st.shutdown_server_stack( ss )

def test_algorithm_get_nodeResourceList_from_monitor():
    host = st.LOCALHOST
    port = st.get_port()
    alg = Algorithm(host, port)
    mon = Monitor(host, port+1)
    rack = Rack(host, port+2)

    rack.algorithm_addr = alg.addr()
    alg.monitor_addr = mon.addr()

    ss = [ alg, mon, rack ]


    pm1 = { "name": "pm1", "memory": 3024, "disk": 100 } 
    pm2 = { "name": "pm2", "memory": 9024, "disk": 30  }
    pm3 = { "name": "pm3", "memory": 14024, "disk": 400 }
    pm4 = { "name": "pm4", "memory": 6024, "disk": 300 }
    testlist = [pm1,pm2,pm3, pm4]
    # let monitor return test data
    def dummyNodeResourceList( rack_addr ):
        return testlist[:]
    mon.getNodeResourceList = dummyNodeResourceList

    # server up
    st.start_server_stack( ss, hint=True, sleeptime=4 )

    # let rack ask alg, and alg ask monitor, then alg sorted it
    # init alg use best fit for memory factor
    vm_attr = [1,2,3,4,5,5024,40,8,9]  # memory: 5024, disk=40
    result_list = rack.selectNodeList( vm_attr )

    print("dump testlist: "),
    print(testlist)

    print("dump result_list: "),
    print(result_list)

    expected_list = [pm3, pm4]
    print("dump expected_list:"),
    print( expected_list)

    # server down
    st.shutdown_server_stack( ss )


    assert expected_list == result_list



    




    
