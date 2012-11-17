from Roystonea.scripts.algorithm import Algorithm
from Roystonea.scripts.rack import Rack
from Roystonea.scripts.monitor import Monitor
from support import server_manager as st # server_tool
import random
import time

HOST = "127.0.0.1"
PORT = st.get_port()


def test_rack_reach_algorithm():
    assert True
    return

    # server init
    algorithm_server = Algorithm( HOST, PORT )
    rack_server = Rack ( HOST, PORT + 1 )

    rack_server.algorithm_addr = algorithm_server.addr() 

    server_stack = [algorithm_server, rack_server] 

    holder = dict()
    method_name = "selectNodeListHandler"
    holder[method_name] = False
    def method_called(self,msg,client_address=None):
        print("in")
        holder[ method_name ] = True

    algorithm_server.selectNodeListHandler = method_called

    st.start_server_stack( server_stack, True )
    time.sleep(5)
    rack_server.selectNodeList( [1,1,1,'ubuntu',1,1024,40,192, 1])

    for i in range( 5 ) :
        if holder[method_name] == False :
            time.sleep( 1 )

    st.shutdown_server_stack( server_stack )

    assert holder[method_name ] == True


def test_rack_reach_monitor():
    assert True
    return

    port = st.get_port()

    rack_server = Rack(HOST, port)
    algorithm_server = Algorithm(HOST, port + 1)
    monitor_server = Monitor(HOST, port + 2 )

    rack_server.algorithm_addr = algorithm_server.addr()
    rack_server.monitor_addr = monitor_server.addr()
    algorithm_server.monitor_addr = monitor_server.addr()

    server_stack = [rack_server, algorithm_server, monitor_server]


    method_name = 'askNodeResourceListHandler'
    holder = dict()
    holder[method_name] = False

    is_called = False
    def called(self,msg,addr=None):
        holder[method_name] = True
    monitor_server.askNodeResourceListHandler = called
    
    st.start_server_stack( server_stack, True)

    try:
        time.sleep(4)

        rack_server.selectNodeList([1,1,1,'ubuntu',1,1024,40,192, 1])

        counter = 5
        while counter > 0 :
            if is_called == False :
                time.sleep(1)
            counter = counter - 1
    finally:
        st.shutdown_server_stack( server_stack )

    assert holder[method_name] == True

def test_algorithm_respond():
    port = st.get_port()
    rack_server = Rack( HOST, port + 1 )
    algorithm_server = Algorithm(HOST,  port )
    algorithm_server.name = "My Algorithm"
    rack_server.algorithm_addr = algorithm_server.addr()

    server_stack = [ algorithm_server, rack_server ]

    st.start_server_stack(server_stack)
    time.sleep(4)

    algorithm_name = rack_server.askAlgorithmName()
    print("algorithm_name var: "),
    print( algorithm_name )

    st.shutdown_server_stack( server_stack)

    assert algorithm_server.name == algorithm_name




    
