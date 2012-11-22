from Roystonea.scripts.monitor import Monitor
from Roystonea.scripts.coordinator import Coordinator
from Roystonea.scripts.include.hierachy import *
from support import server_manager as st
from time import sleep

def test_monitor():
    host = st.LOCALHOST
    port = st.get_port()
    m = Monitor( host, port)
    c = Coordinator( host, port+1)

    m.coordinator_addr = c.addr()

    test_hierachy = Hierachy()

    node1 = NodeDaemonUnit( "node1", host, port+2, "roystonea01" )
    node2 = NodeDaemonUnit( "node2", host, port+3, "roystonea02" )
    node3 = NodeDaemonUnit( "node3", host, port+4, "roystonea03" )
    test_hierachy.add_daemon( node1 )
    m.hiearchy = test_hierachy

    ss = [m,c]
    st.start_server_stack( ss, True, 4 )
    m.monitor( ["roystonea01","roystonea02", "roystonea03"])


    st.shutdown_server_stack( ss )


