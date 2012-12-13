from include.base_server import BaseServer
from include import message
# //
# resourceList spec
#    a list of resourceUnit
# //
# resourseUnit sepc
#   type
#   name 
#   host
#   port
#   memory 
#   disk
#   minimalMemory
#   minimalDisk (only exists in Rack,Cluster,Cloud )
# //
# vmInfo sepc
#   at least config_memory, config_disk
# //
# algorithmReturn spec
#   a list of resourceUnit with order
# //
# askRackReq( "vmInfo":
#             "ParentUnit": Unit) 
# //
# askRackRes( "UnitList": a list of resourceUnits with order )


class Algorithm(BaseServer):

    level = "algorithm"

    def __init__(self, host, port):
        super(Algorithm, self).__init__(host, port)
        self.node_addr = None
        self.rack_addr = None
        self.cluster_addr = None
        self.monitor_addr = None

    def register_handle_functions(self):
        self.register_handle_function("AlgorithmSelectClusterListReq", self.selectClusterListHandler)
        self.register_handle_function("AlgorithmSelectRackListReq", self.selectRackListHandler)
        self.register_handle_function("AlgorithmSelectNodeListReq", self.selectNodeListHandler)

    def selectNodeListHandler(self, msg, client_address=None):
        # get resource list
        node_resource_list = self.ask_children_resource_list( msg.caller_address, parent_type="rack" )
        
        # get vm_attr
        vm_attr = msg

        # process
        result_ordered_unit_list = self.alg_best_fit( vm_attr, node_resource_list )
        result_ordered_addr_list = self.unit_list_to_addr_list ( result_ordered_unit_list )
        return result_ordered_addr_list 


    def selectClusterListHandler(self, msg, client_address=None):
        node_resource_list = self.ask_children_resource_list( msg.caller_address, parent_type="cloud" )
        
        # get vm_attr
        vm_attr = msg

        # process
        result_ordered_unit_list = self.alg_best_fit( vm_attr, node_resource_list, params={"reverse":True} )
        result_ordered_addr_list = self.unit_list_to_addr_list ( result_ordered_unit_list )
        return result_ordered_addr_list 

    def selectRackListHandler(self, msg, client_address=None):
        node_resource_list = self.ask_children_resource_list( msg.caller_address, parent_type="cluster" )
        
        # get vm_attr
        vm_attr = msg

        # process
        result_ordered_unit_list = self.alg_best_fit( vm_attr, node_resource_list, params={"reverse":True} )
        result_ordered_addr_list = self.unit_list_to_addr_list ( result_ordered_unit_list )
        return result_ordered_addr_list 

    ''' ask children_resource_list of parent_addr from monitor daemon '''
    def ask_children_resource_list(self, parent_addr, parent_type="rack"):
        msg = self.message_class( parent_type )
        req = self.create_message( msg, [parent_addr] )
        children_resource_list = self.send_message( self.monitor_addr, req )
        return children_resource_list.values()

    def message_class( self, parent_type ):
        if parent_type == "cloud":
            return message.MonitorAskClusterResourceListReq
        elif parent_type == "cluster":
            return message.MonitorAskRackResourceListReq
        elif parent_type == "rack":
            return message.MonitorAskNodeResourceListReq
        return None

    ''' 
        Algorithm Implementation
        standard input:
            vm_attr: a dictionary with vm creation set.
            resource_list: a list with resource_list

        standar output:
            a ordered list with address of correct location
        
    '''

    def alg_first_fit(self, vm_attr, resource_list, params=dict() ):
        resource_list = self.enough_fit_vm( vm_attr, resource_list)
        if self.is_param_true( params, 'reverse' ) :
            ordered_list = sorted( resource_list, key = lambda x: x["name"], reverse=True )
        return ordered_list

    def alg_best_fit(self, vm_attr, resource_list, params=dict()):
        resource_list = self.enough_fit_vm( vm_attr, resource_list)
        key_method = self.sorting_factor( params )
        ordered_list = sorted( resource_list, key=key_method, reverse=True ) # max put front
        return ordered_list
        
    def alg_worst_fit(self, vm_attr, resource_list, params=dict()):
        resource_list = self.enough_fit_vm( vm_attr, resource_list)
        facotr = self.sorting_factor( params )
        ordered_list = sorted( resource_list, key=key_method, reverse=False) # max put front
        return ordered_list

        
    ''' tool methods '''
    @staticmethod
    def key_method_memory(r):
        return r.memory
    @staticmethod
    def key_method_disk(r):
        return r.disk

    def is_param_true( self, params, keyname ):
        if params.has_key( keyname )  and params[ keyname ] == True :
            return True
        return False

    def enough_fit_vm(self, vm_attr, resource_list ):
        result_list = list()
        for unit in resource_list:

            if unit.minimal_memory() > vm_attr.config_memory and \
               unit.minimal_disk() > vm_attr.config_disk :
                result_list.append( unit )
        return result_list 
         
    def sorting_factor(self, params): # default factor memory
        if params.has_key('factor') and params['factor'] == 'disk' :
            return Algorithm.key_method_disk
        return Algorithm.key_method_memory

    def unit_list_to_addr_list(self, unit_list):
        addr_list = list()
        for unit in unit_list:
            addr_list.append( unit.addr() )
        return addr_list


def start(port, cluster_addr, rack_addr, node_addr):
    server = Algorithm("127.0.0.1", port)
    server.node_addr = node_addr
    server.rack_addr = rack_addr
    server.cluster_addr = cluster_addr
    server.run()


