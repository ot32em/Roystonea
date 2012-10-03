
# general usage
TYPENAME_CLOUD = 'cloud'
TYPENAME_CLUSTER = 'cluster'
TYPENAME_RACK = 'rack'
TYPENAME_NODE = 'node'
TYPENAME_OTHERS = 'others'
TYPENAME_UNSET = 'unset'
TYPENAME_UNVALID = 'unvalid'
TYPENAME_SEQ = ( TYPENAME_CLOUD, TYPENAME_CLUSTER, TYPENAME_RACK, TYPENAME_NODE )
TYPENAME_ALLSEQ = ( TYPENAME_CLOUD, TYPENAME_CLUSTER, TYPENAME_RACK, TYPENAME_NODE, TYPENAME_UNSET, TYPENAME_UNVALID )

class PM_Entry():
    def __init__(self):
        self.initvar()

    def initvar(self):
        self.level = TYPENAME_UNSET # level(cloud, cluster, rack, node, others)
        self.label = ''             # name of pm
        self.addr = None            # (host, port)
        self.host = ''              # string in domain name or ip
        self.port = 0               # int port
        self.parent_addr = None     # (host, port)
        self.children_addrs = list()# [(host, port), (host, port), ... ]

    def update(self, pme ):
        if pme.level != 'unset' :
            self.setLevel( pme.level )
        if pme.label :
            self.setLabel( pme.label )
        if pme.addr :
            self.setAddr( pme.addr )
        if pme.parent_addr :
            self.setParentAddr(  pme.parent_addr )
        if pme.children_addrs :
            self.setChildrenAddrs( pme.children_addrs )
        return self
    
    def overwrite(self, pme ):
        self = pme
        return self

    def setAll(self, level=TYPENAME_UNSET, label=None, addr=None, parent_addr=None, children_addrs=None):
        level = level.lower()
        if level != TYPENAME_UNSET: 
            self.setLevel(level)
        if label != None:       
            self.setLabel(label)
        if addr != None:
            self.setAddr(addr)
        if parent_addr != None:
            self.setParentAddr(parent_addr)
        if children_addrs != None:
            self.setChildrenAddrs(children_addrs)
        return self

    def setLevel(self, level):
        self.level = level if level in TYPENAME_ALLSEQ else TYPENAME_UNVALID
        return self

    def setLabel(self, label):
        self.label = label 
        return self

    def convAddr(self, addr):
        if type(addr) == str:
            addr = list( addr.split(':') )

        if not type(addr) in (list, tuple):
            raise None

        addr = list(addr)
        addr[1] = int( addr[1] )
        addr = tuple(addr)
        return addr     

    def setAddr(self, addr ):
        if not addr :
            self.addr = None
            self.host = ''
            self.port = 0
            return self
        addr = self.convAddr(addr)
        self.addr = addr
        self.host = addr[0]
        self.port = addr[1]
        return self

    def setParentAddr(self, parent_addr):
        if parent_addr == 'No Parent':
            self.parent_addr = None
        elif parent_addr:
            self.parent_addr = self.convAddr(parent_addr)
        else:
            self.parent_addr = None

        return self

    def setChildrenAddrs(self, children_addrs):

        self.children_addrs = list()

        if children_addrs == 'No Children':
            return self

        if not children_addrs :
            return self

        if type( children_addrs ) == str :
            children_addrs = children_addrs.split(',')
        
        for addr in children_addrs :
            addr = self.convAddr( addr )
            self.children_addrs.append( addr )
        return self

    def convStrAddr(self, addr):
        if not addr :
            return ''
        addr = ( addr[0], str(addr[1]) )
        str_addr = ':'.join(addr)
        return str_addr
   
    def strName(self):
        if self.label :
            s = '{level} ({label})'.format( level = self.level, label = self.label )
        else:
            s = self.level
        return s 

    def strFullname(self):
        s = self.strName() + ' @ ' + self.strAddr()
        return s

    def strAddr(self):
        if self.addr :
            return self.convStrAddr(self.addr)
        return 'addr unsetted'

    def strParentAddr(self):
        if self.parent_addr :
            return self.convStrAddr(self.parent_addr)

        return 'No Parent'

    def strChildrenAddrs(self):
        if not self.children_addrs :
            return 'No Children'
        addrs = list()
        for addr in self.children_addrs :
            addrs.append( self.convStrAddr(addr)  )
        return ','.join( addrs )

    def numChildren(self):
        if self.children_addrs :
            return len(self.children_addrs)
        return 0

    # one row dumping 
    def __repr__(self):
        s = "{fullname}, Parent: {str_parent_addr}, Children Nums: {nums_children_addrs}".format(
            fullname = self.strFullname(), 
            str_parent_addr = self.strParentAddr(),
            nums_children_addrs = self.numChildren() )
        return s
    
    def dump_two_rows(self, indent=0):
        indent_space = ' '*indent*4
        s = indent_space + "{fullname}, Parent: {str_parent_addr}\n".format( fullname = self.strFullname(), str_parent_addr = self.strParentAddr() ) + indent_space + "Children : {str_list_children_addrs}".format(
            fullname = self.strFullname(), 
            str_parent_addr = self.strParentAddr(),
            str_list_children_addrs = self.strChildrenAddrs() )
        return s

    def dump_children_rows(self, indent=0):
        indent_space = indent*4*' '
        s = self.level + " Parent: " + self.strParentAddr() + '\n'
        s += indent_space + " "*4 + self.strFullname() 

        if self.numChildren() == 0 :
            s += ', and has no children.'
        elif self.numChildren() > 0 :
            s += '\n'
            count = 1
            for addr in self.children_addrs :
                childname = 'child %d' % (count) 
                count += 1
                s += indent_space + ' '*8 + "{childname} @ {str_child_addr}".format( childname=childname, str_child_addr=self.convStrAddr( addr ) ) + '\n'
            s = s[0:-1] # trim last \n

        return s
    def dump_pretty(self):
        s = ":"*20 + " PM Relation Dumping " + ":"*20 + '\n'
        s += self.dump_children_rows() + '\n'
        s += ":"*61
        return s
        

    def __eq__(self, comp):
        return (self.level == comp.level) and \
               (self.host  == comp.host ) and \
               (self.port  == comp.port ) and \
               (self.label == comp.label ) and \
               (self.parent_addr == comp.parent_addr ) and \
               (self.children_addrs == comp.children_addrs) 

if __name__ == '__main__' :
    addr = ( '140.112.28.240', 1001 )
    parent_addr = ( '140.112.28.240', 1002 )
    children_addrs = ( ('140.112.28.240', 7003) , ('140.112.28.240', 7004) )
    pm = PM_Entry().setAll(level='Cluster', label='Riva no.1', addr = addr, parent_addr = parent_addr, children_addrs = children_addrs )
    print( pm )
    print( pm.dump_two_rows() )
    print( pm.dump_children_rows() )
