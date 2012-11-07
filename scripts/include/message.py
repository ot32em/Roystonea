from collections import namedtuple

''' Define Message Classes with nametuple

spec: 
    dictionary, 
    key is the class name
    value is a array of string, which is the property will be defined for the class
'''

node_create_vm_attributes = [
        "vmid", "groupid", "vmsubid", "ownerid", 
        "vmtype", "config_cpu", "config_memory", "config_disk", "time_life"]

spec = {
        "ToyReq": ["data"],
        "ToyRes": ["data"],

        "Error": ["msg"],

        "NodeCreateVMReq": node_create_vm_attributes,
        "NodeCreateVMRes": node_create_vm_attributes,
        }

def create_message_class(name, attributes):
    globals()[name] = namedtuple(name, attributes)

for name in spec:
    create_message_class(name, spec[name])
