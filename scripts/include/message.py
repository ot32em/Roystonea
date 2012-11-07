from collections import namedtuple

''' Define Message Classes with nametuple

spec: 
    dictionary, 
    key is the class name
    value is a array of string, which is the property will be defined for the class
'''

callback_attrs = ["caller_address"]

vm_attributes = ["vmid", "groupid", "vmsubid", "vmtype", 
                "config_cpu", "config_memory", "config_disk", "config_lifetime", 
                "ownerid"]

spec = {
        "ToyReq": ["data"],
        "ToyRes": ["data"],

        "Error": ["msg"],

        # Node 
        "NodeCreateVMReq": vm_attributes,
        "NodeCreateVMRes": ["vmid", "status"],

        # Rack
        "RackCreateVMReq": vm_attributes,
        "RackCreateVMRes": ["vmid", "status"],

        # Algorithm
        "AlgorithmSelectRackReq": vm_attributes,
        "AlgorithmSelectNodeReq": vm_attributes,
        "AlgorithmSelectRes": ["ip", "port"]
        }

def values_of_message(message):
    attrs = []
    for field in message._fields:
        attrs.append(getattr(message, field))

    if "Req" in message.__class__.__name__:
        return attrs[:-1]
    return attrs

def create_message_class(name, attributes):
    whole_attrs = attributes[:]
    if "Req" in name:
        whole_attrs += callback_attrs

    globals()[name] = namedtuple(name, whole_attrs)

for name in spec:
    create_message_class(name, spec[name])

