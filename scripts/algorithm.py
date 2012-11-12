from include.base_server import BaseServer
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

    def register_handle_functions(self):
        self.register_handle_function("AlgorithmSelectClusterReq", self.selectClusterHandler)
        self.register_handle_function("AlgorithmSelectRackReq", self.selectRackHandler)
        self.register_handle_function("AlgorithmSelectNodeReq", self.selectNodeHandler)

    def selectClusterHandler(self, msg, client_address=None):
        return self.cluster_addr

    def selectRackHandler(self, msg, client_address=None):
        # pass
        # # ask coordinator for rack's resource
        # racks = getRackResourcesFromCluster( client_address )
        # vminfo = msg['vminfo']
        return self.rack_addr

    def _getRackResourcesFromCluster( client_address ):
        monitorAddress = self.monitor_addr
        return

    def selectNodeHandler(self, msg, client_address=None):
        return self.node_addr

    def algorithmFirstFit(self, vmInfo, resourceList, params=dict() ):
        availiableList = self._filterAvalibaleResources( vmInfo, resourceList )
        if self.isParamTrue( params, 'reverse' ) :
            priorityOrder = sorted( availiableList, reverse=True )
        return priorityOrder

    def algorithmBestFit(self, vmInfo, resourceInfoList, params=dict()):
        availiableList = self._filterAvalibaleResources( vmInfo, resourceList )
        factor = self._getFactor( params )
        priorityOrder = sorted( availiableList, key=lambda resource: resource[factor], reverse=True ) # max put front
        
    def algorithmWorstFit(self, vmInfo, resourceInfoList, params=dict()):
        availiableList = self._filterAvalibaleResources( vmInfo, resourceList )
        factor = self._getFactor( params )
        priorityOrder = sorted( availiableList, key=lambda resource: resource[factor] ) # max put back
        
    def _isParamTrue( self, params, keyname ):
        if params.has_key( keyname )  and params[ keyname ] == True :
            return True
        return False

    def _filterAvailibleResources(self, vmInfo, resourceList, params ):
        resultList = list()
        for resourceInfo in resourceInfoList:
            if resourceInfo.type == 'Node' :
                resourceInfo['minimalMemory'] = resourceInfo['memory']
                resourceInfo['minimalDisk'] = resourceInfo['disk']

            if resourceInfo['minimalMemory']  > vmInfo['config_memory'] and  \
                resourceInfo['minimalDisk'] > vmInfo['config_disk']:
                resultList.append( resourceInfo )
        return resultList
        
    def _getFactor(self, params):
        if params.has_key('factor') and params['factor'] == 'disk' :
            return 'disk'
        return 'memory'

    def _enough(self, vmInfo, resourceInfo ):
        if vmInfo['config_memory'] > resourceInfo['memory'] and vmInfo['config_disk'] > resourceInfo['disk'] :
            return True
        return False

def start(port, node_addr, rack_addr, cluster_addr):
    server = Algorithm("127.0.0.1", port)
    server.node_addr = node_addr
    server.rack_addr = rack_addr
    server.cluster_addr = cluster_addr
    server.run()
