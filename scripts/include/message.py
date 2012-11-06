from collections import namedtuple

node_create_vm_attributes = [
        "vmid", "groupid", "vmsubid", "ownerid", 
        "vmtype", "config_cpu", "config_memory", "config_disk", "time_life"]

spec = {
        "NodeCreateVMReq": node_create_vm_attributes,
        "NodeCreateVMRes": node_create_vm_attributes,
        }

def create_message_class(name, attributes):
    globals()[name] = namedtuple(name, attributes)

for name in spec:
    create_message_class(name, spec[name])
