'''
## Message.Document ##
Node:
    NodeVirtualMachineManagerCreateVMres()
    NodeDatabaseSubsystemAddPortReq()

Rack:
    RackAlgorithmResourceInformationReq()
    RackAlgorithmReq()
    RackVirtualMachineManagerCreateVMreq()
    RackVirtualMachineManagerCreateVMres()

Cluster:
    ClusterVirtualMachineManagerCreateVMreq()
    ClusterDatabaseSubsystemCreateVMres()

Cloud:

Coordinator:
    DatabaseSubsystemCreateVMreq()

SubsystemManager:
    NetworkingSubsystemPortMappingReq()
    MonitoringSubsystemPMreq()

Algorithm:
    
'''
# Common Package #
class VmInfo():
    def __init__(self, **kargs):
        self.vmid = kargs['vmid']
        self.groupnum= kargs['groupnum']
        self.vmnum = kargs['vmnum']
        self.vmname = kargs['vmname']

        self.owner = kargs['owner']
        self.vmtype = kargs['vmtype']
        self.config_cpu = kargs['config_cpu']
        self.config_mem = kargs['config_memory']
        self.config_disk = kargs['config_disk']
        self.time_life = kargs['time_life']

'''Node'''

class CreateVmByNodeReq():
    def __init__(self, **kargs):
        self.vmid = kargs['vmid']
        self.groupid = kargs['groupid']
        self.vmsubid = kargs['vmsubid']
        self.ownerid= kargs['ownerid']

        self.vmtype= kargs['vmtype']
        self.config_cpu = kargs['config_cpu']
        self.config_memory = kargs['config_memory']
        self.config_disk = kargs['config_disk']
        self.config_lifetime = kargs['config_lifetime']
        
class CreateVmByRackReq():
    def __init__(self, **kargs):
        self.vmid = kargs['vmid']
        self.groupid = kargs['groupid']
        self.vmsubid = kargs['vmsubid']
        self.ownerid= kargs['ownerid']

        self.vmtype= kargs['vmtype']
        self.config_cpu = kargs['config_cpu']
        self.config_memory = kargs['config_memory']
        self.config_disk = kargs['config_disk']
        self.config_lifetime = kargs['config_lifetime']


class NodeVirtualMachineManagerCreateVMres():
    def __init__(self, **kargs):
        self.vm_id = kargs['vm_id']
        self.status = kargs['status']

class NodeDatabaseSubsystemAddPortReq():
    def __init__(self, **kargs):
        self.vm_id = kargs['vm_id']
        self.vm_name = kargs['vm_name'] 
        self.owner = kargs['owner']
        self.vm_port = kargs['vm_port']

'''Rack'''
class RackAlgorithmResourceInformationReq():
    def __init__(self, **kargs):
        self.rack = kargs['rack']

class RackAlgorithmReq():
    def __init__(self, **kargs):
        self.vm_id = kargs['vm_id']
        self.cpu = kargs['cpu']
        self.mem = kargs['mem']
        self.disk = kargs['disk']
        self.pm_resource_list = kargs['pm_resource_list']

class RackVirtualMachineManagerCreateVMreq():
    def __init__(self, **kargs):
        self.vm_id = kargs['vm_id']
        self.group_num = kargs['group_num']
        self.vm_num = kargs['vm_num']
        self.vm_name = kargs['vm_name']
        self.owner = kargs['owner']
        self.type = kargs['type']
        self.cpu = kargs['cpu']
        self.mem = kargs['mem']
        self.disk = kargs['disk']

class RackVirtualMachineManagerCreateVMres():
    def __init__(self, **kargs):
        self.vm_id = kargs['vm_id']
        self.status = kargs['status']

'''Cluster'''
class ClusterVirtualMachineManagerCreateVMreq():
    def __init__(self, **kargs):
        self.vm_id = kargs['vm_id']
        self.group_num = kargs['group_num']
        self.vm_num = kargs['vm_num']
        self.vm_name = kargs['vm_name']
        self.owner = kargs['owner']
        self.type = kargs['type']
        self.cpu = kargs['cpu']
        self.mem = kargs['mem']
        self.disk = kargs['disk']

class ClusterDatabaseSubsystemCreateVMres():
    def __init__(self, **kargs):
        self.vm_id = kargs['vm_id']
        self.status = kargs['status']

'''Cloud'''


'''Coordinator'''
class DatabaseSubsystemCreateVMreq():
    def __init__(self, **kargs):
        self.vm_id = kargs['vm_id']
        self.group_num = kargs['group_num']
        self.vm_num = kargs['vm_num']
        self.vm_name = kargs['vm_name']
        self.owner = kargs['owner']
        self.type = kargs['type']
        self.cpu = kargs['cpu']
        self.mem = kargs['mem']
        self.disk = kargs['disk']

'''SubsystemManager'''
class NetworkingSubsystemPortMappingReq():
    def __init__(self, **kargs):
        self.vm_port = kargs['vm_port']
        self.vm_id = kargs['vm_id']
        self.vm_name = kargs['vm_name']
        self.owner = kargs['owner']

class MonitoringSubsystemPMreq():
    def __init__(self, **kargs):
        pass

''' Algorithm '''    


''' Command '''
class ShutdownReq():
    def __init__(self, **kargs):
        self.rack = kargs["rack"]
        self.node = kargs["node"]
        self.vm_id = kargs["vm_id"]
        self.vm_name = kargs["vm_name"]
       
class ShutdownRes():
    def __init__(self, **kargs):
        self.msg = kargs["msg"]
        self.hostname = kargs["hostname"]
        self.vm_id = karfs["vm_id"]

class CmdShutdownReq():
    def __init__(self, **kargs):
        self.after_secs = kargs.get('after_secs', 0 )
        self.chain_shutdown = kargs.get('chain_shutdown', False )

class CmdShutdownRes():
    pass

class CmdShutdownChildrenReq():
    def __init__(self, **kargs):
        self.chain_shutdown = kargs.get('chain_shutdown', False )
class CmdShutdownChildrenRes():
    pass

class CmdShutdownTheReq():
    def __init__(self, **kargs):
        self.dest_addr = kargs['dest_addr']
        self.chain_shutdown = kargs.get('chain_shutdown', False )

class CmdShutdownTheRes():
    pass

class CmdPingReq():
    pass
class CmdPingRes():
    pass

class CmdGetPingReq():
    def __init__(self, **kargs):
        self.dest_addr = kargs['dest_addr']
        self.times = kargs.get('times', 4)
class CmdGetPingRes():
    def __init__(self, **kargs):
        self.msg = kargs['msg']

class CmdGetThePMRelationReq():
    def __init__(self, **kargs):
        self.dest_addr = kargs['dest_addr']

class CmdGetThePMRelationRes():
    def __init__(self, **kargs):
        self.pm_relation = kargs['pm_relation']
        self.dump_one_row = kargs['dump_one_row']
        self.dump_two_rows = kargs['dump_two_rows']
        self.dump_children_rows = kargs['dump_children_rows']
        self.dump_pretty = kargs['dump_pretty']

class CmdGetChildrenPMRelationsReq():
    pass

class CmdGetChildrenPMRelationRes():
    def __init__(self, **kargs):
        self.res_pm_relations = kargs['res_pm_relations']

class CmdGetPMRelationReq():
    pass

class CmdGetPMRelationRes():
    def __init__(self, **kargs):
        self.pm_relation = kargs['pm_relation']
        self.dump_one_row = kargs['dump_one_row']
        self.dump_two_rows = kargs['dump_two_rows']
        self.dump_children_rows = kargs['dump_children_rows']
        self.dump_pretty = kargs['dump_pretty']

class CmdSetPMRelationReq():
    def __init__(self, **kargs):
        self.pm_relation = kargs['pm_relation']

class CmdSetPMRelationRes():
    pass

class CmdSetThePMRelationReq():
    def __init__(self, **kargs):
        self.dest_addr = kargs['dest_addr']
        self.pm_relation = kargs['pm_relation']

class CmdSetThePMRelationRes():
    pass

class CmdUpdatePMRelationReq():
    def __init__(self, **kargs):
        self.pm_relation = kargs['pm_relation']

class CmdUpdatePMRelationRes():
    pass


class CmdShutdownChildrenReq():
    pass

class CmdShutdownChildrenRes():
    pass

class CmdShutdownTheChildrenReq():
    def __init__(self, **kargs):
        self.dest_addr = kargs['dest_addr']

class CmdShutdownTheChildrenRes():
    pass


class CmdGetParentReq():
    pass

class CmdGetParentRes():
    def __init__(self, **kargs):
        self.parent_addr = kargs['parent_addr']

class CmdSetParentReq():
    def __init__(self, **kargs):
        self.parent_addr = kargs['parent_addr']
class CmdSetParentRes():
    pass

class CmdGetChildrenReq():
    pass

class CmdGetChildrenRes():
    def __init__(self, **kargs):
        self.children_addrs = kargs['children_addrs']

class CmdSetChildrenReq():
    def __init__(self, **kargs):
        self.children_addrs = kargs['children_addrs']

class CmdSetChildrenRes():
    pass

class CmdAddChildReq():
    def __init__(self, **kargs):
        self.child_addr = kargs['child_addr']

class CmdAddChildRes():
    pass

''' Gerneral '''
class Error():
    def __init__(self, **kargs):
        self.msg = kargs['msg']

''' Algorithm '''    
# All data use String to transmit except pm_list, which is a list.
class SendToAlgorithm():
    def __init__(self, **args):
        self.vm_name = args["vm_name"]
        self.memory_size = args["memory_size"]
        self.disk_size = args["disk_size"]
        self.pm_list = args["pm_list"]

class ReceiveFromAlgorithm():
    def __init__(self, **args):
        self.vm_name = args["vm_name"]
        self.pm_source = args["pm_source"]
        self.pm_destination = args["pm_destination"]
        self.remain_memory = args["remain_memory"]
        self.remain_disk = args["remain_disk"]

''' Test '''
class Test():
    def __init__(self, **args):
        self.message = args["message"]
