'''
This is Cluster.py
Remember to type "HOST" and "PORT" arguments when execute Coordinator.py
ex. "python Coordinator.py 192.168.10.1 10000"

## You have to convert "HOST" to "int" type

by Ot Chen, Teddy, 2012/03/07
'''


from scripts.include.CommonHandler import  passArguments
from scripts.include.Client import *
from time import sleep
import socket

from scripts.include import CommonHandler, Message

class Cluster(CommonHandler):
    ''' custom init variable '''
    num_rthreads = 4
    FILENAME_MY_CONFIG = 'Cluster_cfg'
    level = 'cluster'
    round_robin_machine = -1 # teddy custom variable
  
    def __init__(self, host, port):
        CommonHandler.__init__(self, host, port)
        self.dispatch_handlers.update({
            'DatabaseSubsystemCreateVMreq': self.DatabaseSubsystemCreateVM,
            'RackVirtualMachineManagerCreateVMres': self.RackVirtualMachineManagerCreateVM,
        })
        self.startup_functions.extend((
            self.sayHello, # hello function 
        ))
   
    def DatabaseSubsystemCreateVM(self, req):
       
        # use vm_num to decide how to round robin to Rack
        # 3 is number of machines, replace with len(Machine_list)        
        if req.vm_num == 1:
            self.round_robin_machine = (self.round_robin_machine + 1) % 3 
        ### use hypervisor to replace!!!

        try:
            msg = Message.ClusterVirtualMachineManagerCreateVMreq(
                    vm_id = req.vm_id,
                    group_num =  req.group_num,
                    vm_num =  req.vm_num,
                    vm_name =  req.vm_name,
                    owner =  req.owner,
                    type =  req.type,
                    cpu =  req.cpu,
                    mem =  req.mem,
                    disk =  req.disk,
                    )
        
            rack_address = 'roystonea02', 9600
            sendonly_message(rack_address, msg) 
            
        except socket.error as e:
            print 'socket error'
            sleep(5)
        
    def RackVirtualMachineManagerCreateVM(self, req):
        msg = Message.ClusterDatabaseSubsystemCreateVMres(
                vm_id = req.vm_id,
                status = req.status
                )
        
        coordinator_address = 'roystonea01', 9000
        sendonly_message(coordinator_address, msg)

    def sayHello(self):
        print 'Hello'
    
if __name__ == '__main__':
    host, port, console_off = passArguments()
    mymachine = Cluster( host, port )
    mymachine.run(console_off)

