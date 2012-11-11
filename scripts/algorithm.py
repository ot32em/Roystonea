from include.base_server import BaseServer

class Algorithm(BaseServer):

    level = "algorithm"

    def __init__(self, host, port):
        super(Algorithm, self).__init__(host, port)

        self.node_addr = None
        self.rack_addr = None

    def register_handle_functions(self):
        self.register_handle_function("AlgorithmSelectRackReq", self.selectRackHandler)
        self.register_handle_function("AlgorithmSelectNodeReq", self.selectNodeHandler)


    def selectRackHandler(self, msg, client_address=None):
# ask coordinator for rack's resource
        racks = getRackResourcesFromCluster( client_address )
        vminfo = msg['vminfo']
        return self.rack_addr

    def algorithmFirstFit(self, vmInfo, resourceDict, params=dict() ):
        priorityOrder = list()
        for i in self._getRange( len( resourceInfoList), params ):
            if self._enough( vmInfo, resourceInfoList[i] ) :
                priorityOrder.append( i )
        return priorityOrder
dfj
    def algorithmBestFit(self, vmInfo, resourceInfoList, params=dict()):
        factor = self._getFactor( params )
        maxValue = -1
        maxI = -1
        
        avaliableResourceInfoList
        for i in resourceInfoList :
            if 
        
        
    def _getFactor(self, params):
        if params.has_key('factor') and params['factor'] == 'disk' :
            return 'disk'
        return 'memory'


    def _getRange(self, length, params ):
        if params.has_key("reverse") and params['reverse'] == True:
            return xrange( length - 1, 0 - 1, -1 )
        return xrange( 0, length )

    def _enough(self, vmInfo, resourceInfo ):
        if vmInfo['config_memory'] > resourceInfo['memory'] and vmInfo['config_disk'] > resourceInfo['disk'] :
            return True
        return False

    def selectNodeHandler(self, msg, client_address=None):
        return self.node_addr
