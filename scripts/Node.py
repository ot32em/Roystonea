'''
This is Node.py
Remember to type "HOST" and "PORT" arguments when execute Node.py
ex. "python Node.py 192.168.10.1 10000"

## You have to convert "HOST" to "int" type

by Elalic, Ot Chen, llegalkao, Teddy, 2012/03/07
'''

from scripts.include.CommonHandler import  passArguments
from scripts.include.Client import *

# from vm_manager.vm_ubuntu_manager import VMUbuntuManager
from scripts.include.CommonHandler import CommonHandler
from scripts.include import Message

class Node(CommonHandler):
    ''' custom init variable '''
    FILENAME_MY_CONFIG = 'Node_cfg'
    num_rthreads = 100
    level = "node"

    def __init__(self, host, port):
        CommonHandler.__init__(self, host, port)
        self.dispatch_handlers.update({
            'RackVirtualMachineManagerCreateVMreq': self.RackVirtualMachineManagerCreateVM,
            'Test': self.test
        })
        self.startup_functions.extend((
            self.sayHello,
        ))

    def test(self, req):
        print req.message
    
    def RackVirtualMachineManagerCreateVM(self, req):
        
        print 'vm id: ', req.vm_name

        if req.type == 'mpi':
            pass
        elif req.type == 'hadoop':
            pass
        elif req.type == 'storage':

            pass
        elif req.type == 'apache':
            msg = Message.NodeDatabaseSubsystemAddPortReq(
                    vm_id = req.vm_id,
                    vm_name = req.vm_name,
                    owner = req.owner,
                    vm_port = 80
            )
            
            coordinator_address = 'roystonea01', 9000
            
            res = send_message(coordinator_address, msg)

        elif req.type == 'ubuntu':
            ubuntu = VMUbuntuManager(
                    req.vm_id, 
                    req.owner, 
                    req.group_num, 
                    req.vm_num, 
                    req.mem, 
                    req.disk, 
                    req.cpu, 
                    None)

        elif req.type == 'hbase':
            pass    
        else: 
            pass
       
        # need to check VM start or not!!!
        msg = Message.NodeVirtualMachineManagerCreateVMres(
               vm_id = req.vm_id,
               status = 'success'
                )

        rack_address = 'roystonea02', 9600
        sendonly_message(rack_address, msg)

    def sayHello(self):
        print 'hello'


def start(host, port):
    node = Node(host, port)
    node.run(True)

if __name__ == '__main__':
    host, port, console_off = passArguments() 
    mymachine = Node( host, port )
    mymachine.run(console_off)

