from Roystonea.scripts.monitor import Monitor
from Roystonea.scripts.include.hierachy import *
from support import server_manager as st
from time import sleep

def test_monitor():
    host = st.LOCALHOST
    port = st.get_port()
    m = Monitor( host, port)

    test_hierachy = Hierachy()

    node1 = NodeDaemonUnit( "node1", host, port+1, "140.112.28.240" )
    test_hierachy.add_daemon( node1 )
    m.hiearchy = test_hierachy

    ss = [m]
    m.monitor( ["140.112.28.240"])
#    st.start_server_stack( ss, True, 4 )
#    st.shutdown_server_stack( ss )


