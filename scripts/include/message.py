from collections import namedtuple

''' Define Message Classes with nametuple

spec: 
    dictionary, 
    key is the class name
    value is a array of string, which is the property will be defined for the class
'''

request_attrs = ["caller_address", "request_id"]
response_attrs = ["request_id"]

vm_attributes = ["vmid", "groupid", "vmsubid", "vmtype", 
                "config_cpu", "config_memory", "config_disk", "config_lifetime", 
                "ownerid"]

spec = {
        "ToyReq": ["data"],
        "ToyRes": ["data"],

        "Error": ["msg"],

        # Subsystem
        "SubsystemPortMappingReq": ["data"],

        # Node 
        "NodeCreateVMReq": vm_attributes,
        "NodeCreateVMRes": ["vmid", "status"],

        # Rack
        "RackCreateVMReq": vm_attributes,
        "RackCreateVMRes": ["vmid", "status"],

        # Cluster
        "ClusterCreateVMReq": vm_attributes,
        "ClusterCreateVMRes": ["vmid", "status"],

        # Algorithm
        "AlgorithmSelectClusterReq": vm_attributes,
        "AlgorithmSelectRackReq": vm_attributes,
        "AlgorithmSelectNodeReq": vm_attributes,
        "AlgorithmSelectRes": ["address"]
        }

def values_of_message(message):
    attrs = []
    for field in message._fields:
        attrs.append(getattr(message, field))

    if "Req" in message.__class__.__name__:
        return attrs[:-len(request_attrs)]
    elif "Res" in Message.__class__.__name__:
        return attrs[:-len(response_attrs)]

    return attrs

def create_message_class(name, attributes):
    whole_attrs = attributes[:]
    if "Req" in name:
        whole_attrs += request_attrs
    elif "Res" in name:
        whole_attrs += response_attrs

    globals()[name] = namedtuple(name, whole_attrs)

for name in spec:
    create_message_class(name, spec[name])

