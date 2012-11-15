import threading
import socket
import random
import time

def start_server_stack(server_stack, hint=False, sleeptime=4):
    for server in server_stack:
        if hint :
            server.setHintLaunched()
        t = threading.Thread(target = server.run)
        t.start()

    time.sleep( sleeptime )


def shutdown_server_stack(server_stack):
    for server in reversed(server_stack):
        server.shutdown()

def get_port():
    port = random.randrange( 20000,25000)
    port = get_unused_port( port )
    return port

def get_unused_port( test_port ):
    a = socket.socket(socket.AF_INET)
    test_times = 100
    for i in xrange( test_times ):
        if _test_port_used( test_port ) :
            test_port = test_port + 1
        else :
            return test_port
    return None

def _test_port_used(port):
    try:
        a = socket.socket( socket.AF_INET )
        a.bind( ("127.0.0.1", port ) )
        a.close()
        return False
    except socket.error as e :
        return True


LOCALHOST = "127.0.0.1"
