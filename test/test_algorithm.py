import sys
from rootpath import ROYSTONEA_ROOT
import support.server_manager as server_manager

sys.path.append( ROYSTONEA_ROOT )
from scripts.algorithm import Algorithm
from scripts.monitor import Monitor
import socket
# Test algorithm daemon

a = [1,2,3,4]

# memory unit: KB, disk unit: KB
KB = 1
GB = 1024 * 1024 * KB
pm01 = { "name": "hostmachine1", "memory":  1*GB, "disk":  40*GB, "host": "roystonea01" }
pm02 = { "name": "hostmachine2", "memory": 13*GB, "disk": 400*GB, "host": "roystonea02" }
pm03 = { "name": "hostmachine3", "memory": 12*GB, "disk":  10*GB, "host": "roystonea03" }
pm04 = { "name": "hostmachine4", "memory": 10*GB, "disk": 500*GB, "host": "roystonea04" }
pmInfoList = [pm01, pm02, pm03, pm04]

vm01 = { "config_memory": 0.5*GB, "config_disk":  5*GB } # fit 1, 2, 3, and 4
vm02 = { "config_memory":   2*GB, "config_disk": 11*GB } # fit 2, 3, and 4
vm03 = { "config_memory": 0.5*GB, "config_disk": 20*GB } # fit 1, 2, and 4

HOST = "127.0.0.1"
PORT = 7500



def test_success():
    assert a[0] == 1
    assert a[1] == 2
    assert a[2] == 3
    assert a[3] == 4

def test_connected():

# server stack
    rack = Rack( HOST, PORT)
    algo = Algorithm( HOST, PORT+1)
    monitor = Monitor( HOST, PORT+2)
    server_stack = [algo, monitor, rack]

# algo setting
    algo.monitor_addr = monitor.addr()

# rack setting
    rack.algorithm_addr = algo.addr()

    server_manager.start_server_stack( server_stack )

    import time
    t = 0 
    tmax=10
    while 1 :
        time.sleep(3)
        t = t+3
        assert t < tmax
        if rack.hasTestData("testdone"):
            break

    resultNodesList = rack.testData("node_list")
    print( resultNodeList)




def test_first_fit():
    expectedPmListForVm01 = [pm01,pm02,pm03,pm04]
    expectedPmListForVm02 = [pm02,pm03,pm04]
    expectedPmListForVm03 = [pm01,pm02,pm04]
    
def test_first_fit_reverse():
    expectedPmListForVm01 = [pm04, pm03, pm02, pm01]
    expectedPmListForVm02 = [pm04, pm03, pm02]
    expectedPmListForVm03 = [pm04, pm02, pm01]

def test_best_fit_memory():
    expectedPmListForVm01 = [pm02, pm03, pm04, pm01]
    expectedPmListForVm02 = [pm02, pm03, pm04]
    expectedPmListForVm03 = [pm02, pm03, pm01]


def test_best_fit_disk():
    expectedPmListForVm01 = [pm04, pm02, pm01, pm03]
    expectedPmListForVm02 = [pm04, pm02, pm03]
    expectedPmListForVm03 = [pm04, pm02, pm03]


def _assert_equal():

    return True

if __name__ == '__main__':
    print "hi"
    
    test_connected()
    
