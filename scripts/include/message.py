from collections import namedtuple

''' Define Message Classes with nametuple

spec: 
    dictionary, 
    key is the class name
    value is a array of string, which is the property will be defined for the class
'''

request_attrs = ["caller_address", "request_id"]
response_attrs = ["request_id"]

vm_attributes = ["vmid", "groupid", "vmsubid", 
                "vmtype", "config_cpu", "config_memory", "config_disk", "config_lifetime", 
                "ownerid"]

pm_attributes = ["hostmachine", "remainingMemory", "totalMemory",
                 "remainingDisk", "totalDisk", "usagePercentDisk"]

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
        "AlgorithmSelectClusterListReq": vm_attributes + ["cloud_addr"],
        "AlgorithmSelectRackListReq": vm_attributes + ["cluster_addr"],
        "AlgorithmSelectNodeListReq": vm_attributes + ["rack_addr"],
        "AlgorithmSelectNodeListRes": ["node_addr_list"],
        "AlgorithmSelectRes": ["addressList"],

        "AlgorithmAskNameReq": [],

        # Monitor
        "MonitorUnitListRes": ["unit_list"],
        "MonitorAskClusterListReq": ["cloud_unit"],
        "MonitorAskRackListReq": ["cluster_unit"],
        "MonitorAskNodeListReq": ["rack_unit"],
        "MonitorAskNodeListRes": ["cluster_resource_list"],
        "MonitorAskNodeListRes": ["rack_resource_list"],
        "MonitorAskNodeListRes": ["node_resource_list"],
        "MonitorAskClusterResourceListReq": ["cloud_addr"],
        "MonitorAskRackResourceListReq": ["cluster_addr"],
        "MonitorAskNodeResourceListReq": ["rack_addr"],
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

