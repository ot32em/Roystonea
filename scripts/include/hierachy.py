''' 

    @author OT Chen
    @lastmodifted: 2012/11/07
    @description:
        Let the running daemon 
        1.knows self's basic properties like type, host, port, and name.
        2.knows relative relation like parent and children
        3.knows absolute location address like algorithm, coordinator, or SubsystemManager
        from config file, default in ROYSTONEA_ROOT/etc/Hierachy.xml

    @usage: 
    if daemon knows its host and port, get DaemonUnit like 
    ///
        hierachy = Hierachy(xmlfile) 
        myunit = hierachy.getDaemonByAddress( host, port )
    ///
    access your properties, parent, children like
    ///
        myunit.type
        myunit.name
        myunit.host
        myunit.port
        myunit.hostmachine # only Node type

        parentUnit = myunit.parent

        for childName in myunit.children.keys :
            childUnit = myunit.children[childName]
    ///
'''
from rootpath import ROYSTONEA_ROOT
import os
import xml.dom.minidom as xml


class DaemonUnit():
    def __init__(self, typename, name, host, port):
        self.typename = typename
        self.name = name
        self.host = host 
        self.port = port 

    def addr(self):
        return (self.host, int( self.port) )

    def __str__(self):
        return "%s[%s] @%s:%s" % ( self.typename, self.name, self.host, self.port)  

class TreeDaemonUnit(DaemonUnit):
    def __init__(self, typename, name, host, port ):
        DaemonUnit.__init__(self, typename, name, host, port)
        self.parent = None 
        self.children = dict()
        self.isRoot = False

    def addChild( self, treeUnit ):
        if treeUnit == None :
            raise Exception("Config File Error: Null Child.")
        treeUnit.parent = self
        self.children[ treeUnit.name ] = treeUnit

    def removeChild( self, name ):
        self.children[ name ].parent = None
        del self.children[ name ]

    def minimal_memory(self):
        import sys
        minimal_value = sys.maxint
        for unitname in self.children:
            unit = self.children[unitname]
            unit_minimal_memory = unit.minimal_memory()
            if unit_minimal_memory < minimal_value :
                minimal_value = unit_minimal_memory
        return minimal_value
        
    def minimal_disk(self):
        import sys
        minimal_value = sys.maxint
        for unitname in self.children:
            unit = self.children[unitname]
            unit_minimal_disk = unit.minimal_disk()
            if unit_minimal_disk < minimal_value :
                minimal_value = unit_minimal_disk
        return minimal_value

    def memory(self):
        sum_memory = 0
        for unitname in self.children:
            sum_memory = self.children[unitname].disk() + sum_memory
        return sum_memory

    def disk(self):
        sum_disk = 0
        for unitname in self.children:
            sum_disk = self.children[unitname].disk() + sum_disk
        return sum_disk

    @staticmethod
    def _recurDump( daemon, indent=0 ):
        for i in xrange(0, indent):
            print "  ",
        print( daemon )
        for childName in daemon.children.keys() :
            TreeDaemonUnit._recurDump( daemon.children[childName], indent+1 )

    def recurDump( self ):
        TreeDaemonUnit._recurDump( self )

    def __str__(self):
        origin = DaemonUnit.__str__(self)
        if self.isRoot :
            return origin + " isRoot"
        return origin


class NodeDaemonUnit(TreeDaemonUnit):
    # hostmachine: host as string
    def __init__(self, name, host, port, hostmachine=""):
        TreeDaemonUnit.__init__(self, 'Node', name, host, port )
        self.hostmachine = hostmachine

        self._memory = 0
        self._disk = 0

        self._disk_used_percent = 0.0
        
    def __str__(self):
        return DaemonUnit.__str__(self ) + " hostmachine: %s" % ( self.hostmachine ) 

    def minimal_memory(self):
        return self.memory()

    def minimal_disk(self):
        return self.disk()

    def set_memory(self, val):
        self._memory = val
    def set_disk(self, val):
        self._disk = val
    def memory(self):
        return self._memory
    def disk(self):
        return self._disk


class Hierachy():
    def __init__(self, filename = "" ):

        self.daemons = dict()
        self.daemonNames = ["Algorithm", "AlgorithmImp", "SubsystemManager", "Coordinator"]
        self.treeDaemonNames = ["Cloud", "Cluster", "Rack", "Node" ]

        # note only one Daemon 
        self.singleDaemons= dict()

        # if outer daemon
        self.rootDaemon = None
        
        self.filename = filename
        if self.filename :
            self.load(self.filename)

    def load(self, filename):
        self.dom = xml.parse( filename )
        for childNode in self.dom.documentElement.childNodes :
            self.traverse( childNode )

    def traverse(self, node):
        if( node.nodeType != node.ELEMENT_NODE ):
            return None
        if( node.tagName not in self.daemonNames and
            node.tagName not in self.treeDaemonNames ):
            return None

        typename = node.tagName
        name = self._getAttrValue( node, "name")
        host = self._getAttrValue( node, "host")
        port = self._getAttrValue( node, "port")


        daemon = None
        if typename in self.treeDaemonNames:
            if typename == "Node":
                '''----- new Node unit -----'''
                hostmachine = self._getAttrValue( node, "hostmachine" )
                daemon = NodeDaemonUnit( name, host, port, hostmachine )
            else:
                daemon = TreeDaemonUnit( type, name, host, port )
                if self.rootDaemon == None:
                    self.rootDaemon = daemon
                    daemon.isRoot = True
                for childNode in node.childNodes :
                    childDaemon = self.traverse( childNode )
                    if childDaemon == None :
                        continue
                    daemon.addChild( childDaemon )
        else:
            if typename in self.singleDaemons.keys() :
                raise Exception("Config File Error: %s Daemon only exits one instance" % node.tagName )
            daemon = DaemonUnit( typename, name, host, port )
            self.singleDaemons[ typename ]= daemon

        self.add_daemon( daemon )

        return daemon
    
    def add_daemon( self, daemon ):
        self.daemons[ daemon.name ] = daemon
    def add_daemons( self, daemon_list ):
        for d in daemon_list:
            self.add_daemon( d )


    def _getAttrValue(self, node, attrName):
        val = node.getAttribute(attrName)
        if val == None :
            raise Exception( 
        "Config File Error: The Daemon Setting has no {attribute} attribute with tagName: {tagName}".format
            ( attribute = name, tagName = node.tagName  ) )
        return val

    def getAlgorithmDaemon(self):
        return self.singleDaemons['Algorithm']
    
    def getAlgorithmImpDaemon(self):
        return self.singleDaemons['AlgorithmImp']

    def getSubsystemManagerDaemon(self):
        return self.singleDaemons['SubsystemManager']

    def getCoordinatorDaemon(self):
        return self.singleDaemons['Coordinator']

    def getDaemonByAddress(self, host, port=None):
        if isinstance( host, tuple ) and len(host) == 2 :
            port = int(host[1])
            host = host[0]
        
        for name in self.daemons.keys() :
            daemon = self.daemons[name]
            if host == daemon.host and port == daemon.port :
                return daemon
        return None

    def getDaemonByName(self, name):
        if name in self.daemons.keys :
            return self.daemons[name]
        return None

    def getRootDaemon(self):
        return self.rootDaemon

    def getDaemonsByTypes(self, typename ):
        if typename not in self.treeDaemonNames :
            return dict()
        daemons = dict()
        for name in self.daemons.keys() :
            daemon = self.daemons[name]
            if daemon.type == typename :
                daemons[daemon.name ] = daemon
        return daemons

    def dump(self):
        print( "Hierachy Config File: %s" % self.filename )

        algorithmDaemon = self.getAlgorithmDaemon()
        print algorithmDaemon

        algorithmImpDaemon = self.getAlgorithmImpDaemon()
        print algorithmImpDaemon

        subsytem = self.getSubsystemManagerDaemon()
        print subsytem

        coordinator= self.getCoordinatorDaemon()
        print coordinator

        rootDaemon = self.getRootDaemon()
        rootDaemon.recurDump()




if __name__ == '__main__':
    file = "etc/Hierachy.xml"
    abspath = os.path.join( ROYSTONEA_ROOT, file )
    
    hierachy = Hierachy( abspath )
    hierachy.dump()

    ''' 
    usage: 
    if daemon knows its host and port, get DaemonUnit like 
    ///
        hierachy = Hierachy(xmlfile) # The xml-config-file path known from config file.
        myunit = hierachy.getDaemonByAddress( host, port )
    ///
    access your properties, parent, children like
    ///
        myunit.type
        myunit.name
        myunit.host
        myunit.port
        myunit.hostmachine # only Node type

        parentUnit = myunit.parent

        for childName in myunit.children.keys :
            childUnit = myunit.children[childName]
    ///
    '''







