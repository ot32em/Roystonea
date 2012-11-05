'''
This is Rack.py
Remember to type "HOST" and "PORT" arguments when execute Rack.py
ex. "python Rack.py 192.168.10.1 10000"

## You have to convert "HOST" to "int" type

by Elalic, Ot Chen, Radstar Yeh, Teddy, 2012/03/07
'''

from include.CommonHandler import passArguments
from include.Client import *
from time import sleep
import socket
from include.CommonHandler import CommonHandler
from include import Message, Client

class Rack(CommonHandler):
    ''' custom init variable '''
    num_rthreads = 4
    FILENAME_MY_CONFIG = 'Rack_cfg'
    level = 'rack'

    def __init__(self, host, port):
        CommonHandler.__init__(self, host, port)
        self.dispatch_handlers.update({
            'ClusterVirtualMachineManagerCreateVMreq': self.ClusterVirtualMachineManagerCreateVM,
            'NodeVirtualMachineManagerCreateVMres': self.NodeVirtualMachineManagerCreateVM,
            'CreateVmByRackReq': self.CreateVmByRack,
            
		})
        self.startup_functions.extend((
            self.sayHello, # hello function
        ))
    
    def CreateVmByRack(self, CreateVmByRackReq):
        print "accept a createVmByRackReq from Coordinator"
        print("vmid: " + CreateVmByRackReq.vmid) 

        req = CreateVmByRackReq # for shorter alias
        destNodeAddress = ("140.112.28.240", 8001)
#        destNodeAddress = self.selectNodeByAlgorithm( CreateVmByRackReq.vm )
#

    def selectNodeByAlgorithm(self, vm):
        selectNodeReq = Message.SelectNodeReq(vm)
        selectNodeRes = Client.send( selectNodeReq, algorithm.address )
        return selectNodeRes.node


    def ClusterVirtualMachineManagerCreateVM(self, req):
        try:
            # 1. send msg to coordinator to request resource information
            msg = Message.RackAlgorithmResourceInformationReq(
                    rack = 'rack01' # need to know who i am, use config to replace this 'rack01'
            )

            coordinator_address = 'roystonea01', 9000
            resources = send_message(coordinator_address, msg) # resource_dict is dictionary of tuple --> ({}, {}, ...)
            
            resource_list = list()
             
            for resource in resources:
                pm_hostname = resource['host_machine']
                pm_cpu = resource['cpu_available'] 
                pm_mem_MB = resource['mem_available'] / 1024 
                pm_disk_GB = resource['disk_available'] / (1024 * 1024)
                resource_list.append( {'hostname': pm_hostname, 'cpu': pm_cpu, 'mem': pm_mem_MB, 'disk': pm_disk_GB} )
            
            # 2. send msg to algorithm component to schedule VM on PM
            msg = Message.RackAlgorithmReq(
                    vm_id = req.vm_id,
                    cpu = req.cpu,
                    mem = req.mem,
                    disk = req.disk,
                    pm_resource_list = resource_list
            )

            algo_address = 'roystonea02', 9700
            host_machine_for_VM = send_message(algo_address, msg)
            
            print host_machine_for_VM
            
            if host_machine_for_VM == 'No host machine for VM':
                msg.Message.RackVirtualMachineManagerCreateVMres(
                        vm_id = req.vm_id,
                        status = 'fail'
                        )
                
                cluster_address = 'roystonea01', 9500
                sendonly_message(cluster_address, msg)
                
            else:
                # 3. send msg to node to create VM
                msg = Message.RackVirtualMachineManagerCreateVMreq(
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
            
                node_address = host_machine_for_VM, 9800
                sendonly_message(node_address, msg)            
                
        except socket.error as e:
            print 'socket error'
            sleep(5)
    
    def NodeVirtualMachineManagerCreateVM(self, req):
        msg = Message.RackVirtualMachineManagerCreateVMres(
                vm_id = req.vm_id,
                status = req.status
                )

        cluster_address = 'roystonea01', 9500
        sendonly_message(cluster_address, msg)

    def sayHello(self):
        print 'Hello'
        '''
        while True:
            print self.host
            print self.port
            print self.addr
            print self.server.addr
            print self.server.level
            print self.server.pm_relation.label
            print self.server.pm_relation.addr

            sleep(2)
        '''

if __name__ == '__main__':
    host, port, console_off = passArguments() 
    mymachine = Rack( host, port )
    mymachine.run(console_off)

