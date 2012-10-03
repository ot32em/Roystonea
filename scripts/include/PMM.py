'''
*0. Entry
    Entry represent the SERVER's status about label, host, port, parent, children, and
    something dynamic info will add in the future.

    @It's a basic element in the Relation Tree.

    Each variable in Entry likes : entry.label, entry.level, entry.addr, entry.parent_addr, entry.children_addrs 

*1. Colletion
    Collection is a dictionary of { 'cloud': entires, 'cluster': entries, ... }
    entries is a dictionary of { address01: entry01, address02: entry02, ... }

    @We use colletion to globally record the every entries in the hierachy.

    So a normal collection may looks like this   = { 'cloud': 
                                                        { ('localhost', 7001) : entry1,
                                                          ('localhost', 7002) : entry2,
                                                          ('localhost', 7003) : entry3,
                                                          ...
                                                        },
                                                     'cluster':
                                                        { addr04 : entry4,
                                                          addr05 : entry5,
                                                          ...
                                                        },
                                                     'rack' :
                                                        ...
                                                   }

*2. What is S3 
    S3 is a dictionary of { 'nums': nums, 'inserts': inserts, 'update':updates,
                            'delete': deletes }
    [inserts] is a list containing entries
        if entry in new colletion ,but not in old colletion.
        It means We will startup a server according the entry

    [updates] is a list containing entries
        if entry in new colletion and also in old colletion, but the contents
        has difference in here.
        It means We will reconfig the server according the entry.

    [deletes] is a list containing entries
        if entry in old colletion but not in new colletion.
        It means we need to shutdown the server according the entry.

    @We use S3 to see what's changed between new colletion and old colletion.

*3. XML File Hierachy 
    <xml>
    |   <Cloud>
    |   |   <Cluster>
    |   |   |   <Rack>
    |   |   |   |   <Node/>
    |   |   |   |   <Node/>
    |   |   |   |   more nodes...
    |   |   |   </Rack>
    |   |   |   <Rack>
    |   |   |   |   ...
    |   |   |   </Rack>
    |   |   |   more racks ...
    |   |   </Cluster>
    |   |   <Cluster>
    |   |   |   ...
    |   |   </Cluster>
    |   |   more clusters ...
    |   </Cloud>
    |   <Cloud>
    |   |   ...
    |   </Cloud> 
    |   more clouds...
    </xml>

    Each Cloud,Cluster,Rack,and Node has following attributes 
    1.host, 2.port, and 3.label 
    ex: <Cluster host='xxx' port='xxx' label='xxx' >

    @XML has indent architecture to easily read whole Hierachy Relation for admin.

'''
import pexpect
import pxssh
from time import sleep
import datetime
from xml.dom.minidom import parse, Node
import MySQLdb as mysql
from MySQLdb import connect, Error as mError
from scripts.include.PM import *
from scripts.include import CommonHandler, Client, Message

SCRIPTNAME_CLOUD = 'Cloud'
SCRIPTNAME_CLUSTER = 'Cluster'
SCRIPTNAME_RACK = 'Rack'
SCRIPTNAME_NODE = 'Node'

# xml TagName usage
TAGNAME_CLOUD = 'Cloud'
TAGNAME_CLUSTER = 'Cluster'
TAGNAME_RACK = 'Rack'
TAGNAME_NODE = 'Node'

# xml attribute usage
ATTRNAME_HOST = 'host'
ATTRNAME_PORT = 'port'
ATTRNAME_LABEL= 'label'
ATTRNAME_LAST_TIME = 'last_time'

CFGNAME_DB_HOST = 'DBHost'
CFGNAME_DB_NAME = 'DBName'
CFGNAME_DB_USER = 'DBUsername'
CFGNAME_DB_PASS = 'DBPassword'
CFGNAME_DB_TABLE_PM = 'DBTable_PM'
TIMEFORMAT_XMLFILE = '%Y-%m-%d-%H-%M-%S'


class PM_Handler (CommonHandler):
   
    def __init__(self, host, port):

        CommonHandler.__init__(self, host, port)
        self.initCol()
        self.initLastTime()
        self.isStartup = False

        self.startup_functions.extend(  list()
           # ( self.periodlyCheckDB, ) 
        )

   
    def startup(self):
        '''
            1.init last_time(*3)
            2.init colletion(*2) 
            3.update colletion from Database
        '''
        self.current_collection = self.getColByDB()
        self.isStartup = True

    ''' Functions of Init Special Var '''
   
    def initCol(self):
        self.current_collection = { TYPENAME_CLOUD: dict(), TYPENAME_CLUSTER: dict(),
                                    TYPENAME_RACK: dict(), TYPENAME_NODE: dict() }
    def initLastTime(self):
        self.last_time = datetime.datetime(2011,11,1,0,0,0)

    ''' Functions of Dumping some inner status for debugging '''

    def dumpCol(self, dumpLabel='', style="seq", col=None):
        col = self.current_collection if col == None else col
        if dumpLabel :
            print(dumpLabel)

        if style == 'seq':
            for typename in TYPENAME_SEQ:
                if typename in ('unset', 'unvalid' ) :
                    continue
                if typename == 'cloud' :
                    indent = ''
                elif typename == 'cluster' :
                    indent = ' ' * 4
                elif typename == 'rack' :
                    indent = ' ' * 8
                elif typename == 'node' :
                    indent = ' ' * 12

                for addr in col[typename] :
                    print(indent + "%s" %  col[typename][addr] )
        elif style == 'tree': # tree
            print( col[TYPENAME_CLOUD] )
            raw_input()
            times = 0

            for addr in col[TYPENAME_CLOUD] :
                times += 1
                print( "times: %d" % times )
                print( self.__dumpStrTraverse( '', col, TYPENAME_CLOUD, col[TYPENAME_CLOUD][addr] ) )
            print( "times: %d" % times )
    def __dumpStrTraverse(self, result, col, typename, entry, indent = 0):
        
        ''' ==== still has problems I need to fix. ==== '''

        result += indent*'    ' + '%s' % entry + '\n' 
        child_typename = 'unvalid'
        if typename == 'cloud': child_typename = 'cluster'
        if typename == 'cluster': child_typename = 'rack'
        if typename == 'rack': child_typename = 'node'
        
        if len( entry.children_addrs ) > 0 :
            for addr in entry.children_addrs :
                entry = col[child_typename][addr]
                result += self.__dumpStrTraverse( result, col, child_typename, entry, indent+1)
                #except KeyError:
                #    result += ' '*indent + 'Error Entry(TYPE: %s @ (%s, %d)) Not Found in Collection' % ( child_typename, addr[0], addr[1] )
        return result

    ''' Main Functions '''

    def periodlyCheckDB(self, interval):
        '''
            if DB not change OR len(S3(*2)) is 0 => Nothing to do and go back to WAIT 

            1. Get Colletion(*1) from Database
            2. Compare old/new colletions to get S3(*2)
            3. Use S3(*2) to Control startup/reconfig/shutdown status of whole hierachy 
               by sending requests to each machines.
            4. Rerender new XML file to let admin read and for backup purpose
        '''
        self.startup()

        interval = 30
        while True :
            #/ go back waiting if old_last_time == db_last_time /#
            if self.isDBChanged():
                self.loadDB()
            sleep(interval)

    def loadDB(self, sr=True): # sr = sendRequests?
        #/ get collection from database and produce s3 /#
        new_col = self.getColByDB()
        s3 = self.produceS3ByCol(new_col)
        if s3['nums'] == 0 : return

        #/ send startup/reconfig/shutdown orders to each machines /#
        if sr:
            self.sendRequestsByS3(s3)

        #/ update self and backup current collection /#
        self.current_collection = new_col
        self.renderXmlByCol("Relation_%s.xml" % self.last_time )

    def loadXml(self, pathname="relation_xmls/Relation_localhost_debug.xml", overwrite=False, sr=True): # sr = sendRequests?

        '''
            Load XML file (filename supplied in arguments )
            1. Get colletion(*1) from XML file.
            2. Compare new/old colletions(*1) to get S3(*2).
            3. Update colletion(*1) to database by S3(*2).
            4. Update colletion(*1) to self.

            You can specific force=True to override collection(*1) in database.
            
        '''
        #/ erase old data /#
        if overwrite:
            self.wipeDB()
            self.initCol()
        
        #/ get new from xml /*
        xml_col = self.getColByXml(pathname)
        s3 = self.produceS3ByCol(xml_col)
        
        if s3['nums'] == 0 : return

        #/ send startup/reconfig/shutdown orders to each machines /#
        if sr :
            self.sendRequestsByS3(s3)

        #/ update self and sync database /#
        self.current_colletion = xml_col
        sqls = self.produceSqlsByS3(s3)
        self.commitSqls(sqls)

        ''' Tools Functions do what its name called. '''

    def getConnection(self):
        '''
            Not support auto connection close function.
            You must manually close by call connection.close() method.
        '''
        #/ MySQL Arguments assignment /#
        db_host = self.config[CFGNAME_DB_HOST]
        db_name = self.config[CFGNAME_DB_NAME]
        db_user = self.config[CFGNAME_DB_USER]
        db_pass = self.config[CFGNAME_DB_PASS]
        db_table = self.config[CFGNAME_DB_TABLE_PM]
       
        #/ return the connection instance /#
        return  mysql.connect( db_host, db_user, db_pass, db_name)
    def isDBChanged(self):
        '''
            Each time fetch data from database, we will register newest last_time(*3).
            just check whether db_last_time is newer?
        '''
        #/ get db_last_time /#
        con = self.getConnection()
        cur = con.cursor()
        sql = "select `last_time` from `pm` order by `last_time` desc limit 0,1"
        db_last_time = cur.fetchone[0]
        con.close()

        #/ actual compare expression /#
        return self.last_time < db_last_time 
    def wipeDB(self):
        con = self.getConnection()
        cur = con.cursor()
        cur.execute("delete from `pm`")
        con.close()

    def getColByDB(self) :
        '''
            Get Colletion by lookup Database

        '''

        #/ init return colletion object /#
        collection = { TYPENAME_CLOUD: dict(), TYPENAME_CLUSTER: dict(),
                       TYPENAME_RACK: dict(), TYPENAME_NODE: dict() }

        #/ create connection /#
        con = self.getConnection() 
        cur = con.cursor()

        #/ iteratively go through colletion's keys={cloud, cluster, rack, and node} /#
        for typename in TYPENAME_SEQ :

            #/ fetch specific fields at the same level /#
            sql = "select `id`,`level`,`addr`,`label`,`parent_addr`,`children_addrs` from `pm` where `level` = '%s'" % typename
            numrows = cur.execute( sql )

            #/ handler each row of return table /#
            for row in cur.fetchall():
                #/ Data format problems will be handled in PM_Entry::__init__() method /#
                addr = row[2].split(':')
                addr[1] = int( addr[1] )
                addr = tuple(addr)
                pme = PM_Entry()
                pme.setLabel(row[3])
                pme.setLevel(typename)
                pme.setAddr(addr)
                print( 'before set parent ')
                print( pme )
                pme.setParentAddr(row[4])
                print( 'after set parent ')
                print( pme )
                print("row[4]: %s, len: %d" % (row[4], len(row[4]) ) )
                pme.setChildrenAddrs(row[5])
                collection[ typename ][ addr ]  = pme

        #/ register last_time /#
        sql = "select `last_time` from `pm` order by `last_time` desc limit 0,1" 
        
        if cur.execute(sql) > 0 :
            self.last_time = cur.fetchone()[0]
        con.close()

        return collection
    def getColByXml(self, pathname):
        '''
            Parse XML file to produce colletion(*1)
        '''

        #/ Init Return Colletion Variable /#
        cloud_entries = dict()
        cluster_entries = dict()
        rack_entries = dict()
        node_entries = dict()

        #/ Get xml document instance /#
        doc = parse( pathname )
        cloudElements = doc.getElementsByTagName( TAGNAME_CLOUD )
        for cloudElement in cloudElements :
            #/ I use xxx_ga = xxxElement.getAttribute to shorten length of method name /#
            cloud_ga = cloudElement.getAttribute

            #/ get attributes /#
            cloud_host = cloud_ga( ATTRNAME_HOST )
            cloud_port = cloud_ga( ATTRNAME_PORT )
            cloud_addr = (cloud_host, cloud_port) # <-----<-----<-----<-----<-
            cloud_label = cloud_ga( ATTRNAME_LABEL )        # ^
            cloud_parent_addr = None                                       # |
            cloud_children_addrs = list()                                  # ^
                                                                           # |
            for clusterElement in cloudElement.childNodes :                # ^
                if clusterElement.nodeType != Node.ELEMENT_NODE : continue # |
                                                                           # ^ 
                cluster_parent_addr = cloud_addr # -->----->----->----->-----^

                cluster_ga = clusterElement.getAttribute
                cluster_host = cluster_ga( ATTRNAME_HOST )
                cluster_port = cluster_ga( ATTRNAME_PORT )
                cluster_addr = (cluster_host, cluster_port) # <-----<-----<----<
                cluster_label = cluster_ga( ATTRNAME_LABEL ) #  ^
                cluster_children_addrs = list()                             #  |
                                                                            #  ^
                cloud_children_addrs.append( cluster_addr )                 #  |
                                                                            #  ^
                for rackElement in clusterElement.childNodes :              #  |
                    if rackElement.nodeType != Node.ELEMENT_NODE : continue #  ^
                                                                            #  |
                    rack_parent_addr = cluster_addr # ->----->----->----->-----^
                    rack_ga = rackElement.getAttribute
                    rack_host = rack_ga( ATTRNAME_HOST )
                    rack_port = rack_ga( ATTRNAME_PORT )
                    rack_addr = (rack_host, rack_port) # <-----<-----<-----<-----<--
                    rack_label = rack_ga( ATTRNAME_LABEL )       #  ^
                    rack_children_addrs = list()                                #  |
                                                                                #  ^
                    cluster_children_addrs.append( rack_addr )                  #  |
                                                                                #  ^
                    for nodeElement in rackElement.childNodes :                 #  |
                        if nodeElement.nodeType != Node.ELEMENT_NODE : continue #  ^
                                                                                #  |
                        node_parent_addr = rack_addr # ---->----->----->----->-----^
                        node_ga = nodeElement.getAttribute
                        node_host = node_ga( ATTRNAME_HOST )
                        node_port = node_ga( ATTRNAME_PORT )
                        node_addr = ( node_host, node_port )
                        node_label = node_ga( ATTRNAME_LABEL )
                        node_children_addrs = None

                        rack_children_addrs.append( node_addr )

                        # Starting to instanciate nodes, racks, clusters, and cloud
                        node_entries[ node_addr ] = PM_Entry().setAll( level=TYPENAME_NODE,
                                                              addr=node_addr, 
                                                              label=node_label,
                                                              parent_addr=node_parent_addr, 
                                                              children_addrs=node_children_addrs )
                    # } of for nodeElement in rackElement.childNodes :
                    rack_entries[ rack_addr ] = PM_Entry().setAll( level=TYPENAME_RACK,
                                                            addr = rack_addr, 
                                                            label = rack_label,
                                                            parent_addr = rack_parent_addr, 
                                                            children_addrs = rack_children_addrs )
                # } of for rackElement in clusterElement.childNodes 
                cluster_entries[ cluster_addr ] = PM_Entry().setAll( level = TYPENAME_CLUSTER,
                                                            addr = cluster_addr, 
                                                            label = cluster_label,
                                                            parent_addr = cluster_parent_addr, 
                                                            children_addrs = cluster_children_addrs )
            # } of for clusterElement in cloudElement.childNodes : 
            cloud_entries[ cloud_addr ] = PM_Entry().setAll( level = TYPENAME_CLOUD,
                                                    addr = cloud_addr, 
                                                    label = cloud_label,
                                                    parent_addr = cloud_parent_addr, 
                                                    children_addrs = cloud_children_addrs )
        # } of for cloudElement in doc.getElementsByTagName('Cloud')

        #/ pack it /#
        result_collection = { TYPENAME_CLOUD: cloud_entries, TYPENAME_CLUSTER: cluster_entries, TYPENAME_RACK: rack_entries, TYPENAME_NODE: node_entries }
                       
        return result_collection 
    def renderXmlByCol(self, pathname='', collection=None ):
        if pathname == '':
            pathname = "relation_xmls/Relation_%s.xml" % self.last_time.strftime( TIMEFORMAT_XMLFILE )
        if collection == None :
            collection = self.current_collection
        from xml.dom.minidom import Document
        doc = Document()
        root = doc.createElement('xml')
        root.setAttribute( ATTRNAME_LAST_TIME, self.last_time.strftime( TIMEFORMAT_XMLFILE ))
        doc.appendChild(root)
        for cloud in collection[TYPENAME_CLOUD].values() :
            cloud_element = doc.createElement(TAGNAME_CLOUD)
            cloud_element.setAttribute( ATTRNAME_HOST, cloud.host )
            cloud_element.setAttribute( ATTRNAME_PORT, str(cloud.port))
            cloud_element.setAttribute( ATTRNAME_LABEL, cloud.label)
            root.appendChild( cloud_element )
            for cluster in collection[TYPENAME_CLUSTER].values() :
                if cluster.parent_addr != cloud.addr : continue
                cluster_element = doc.createElement(TAGNAME_CLUSTER)
                cluster_element.setAttribute( ATTRNAME_HOST, cluster.host )
                cluster_element.setAttribute( ATTRNAME_PORT, str(cluster.port))
                cluster_element.setAttribute( ATTRNAME_LABEL, cluster.label)
                cloud_element.appendChild( cluster_element )
                for rack in collection[TYPENAME_RACK].values() :
                    if rack.parent_addr != cluster.addr : continue
                    rack_element = doc.createElement(TAGNAME_RACK)
                    rack_element.setAttribute( ATTRNAME_HOST, rack.host )
                    rack_element.setAttribute( ATTRNAME_PORT, str(rack.port))
                    rack_element.setAttribute( ATTRNAME_LABEL, rack.label)
                    cluster_element.appendChild( rack_element )
                    for node in collection[TYPENAME_NODE].values() :
                        if node.parent_addr != rack.addr : continue
                        node_element = doc.createElement(TAGNAME_NODE)
                        node_element.setAttribute( ATTRNAME_HOST, node.host )
                        node_element.setAttribute( ATTRNAME_PORT, str(node.port))
                        node_element.setAttribute( ATTRNAME_LABEL, node.label)
                        rack_element.appendChild( node_element )
        xmlfile = open(pathname, 'w')
        xmlOutput = doc.toprettyxml(indent='    ') 
        xmlfile.writelines( xmlOutput )
        xmlfile.close()
    def produceS3ByCol( self, new_collection) :
        return self.__produceS3By2Col( self.current_collection, new_collection)
    def __produceS3By2Col(self, old_collection, new_collection):
        old_collection = old_collection.copy() # Don't wanna use class ref, because it will be modified.
        insert_entries = list()
        update_entries = list()
        delete_entries = list()

        for typename in TYPENAME_SEQ: #  looply handle cloud, cluster, rack, and node relations
            new_entries = new_collection[typename]
            old_entries = old_collection[typename]
            for new_addr in new_entries:  
                # Situation 1 Condition
                if not new_addr in old_entries:
                    insert_entries.append( new_entries[new_addr] )
                else:
                    old_entry = old_entries[new_addr] # <- here is a place to detect Situation 1 happenned 
                    new_entry = new_entries[new_addr]
                    # Situation 2 Condition: 
                    if old_entry != new_entry :
                        update_entries.append( new_entry )
                    # remove matched addr for handling situation 3
                    del old_entries[new_addr]
            # Situation 3 Condition 
            if old_entries!= None :
                delete_entries.extend( old_entries.values() ) 

        nums = len(insert_entries) + len(update_entries) + len(delete_entries ) 

        return  { 'nums': nums , 'insert': insert_entries, 'update': update_entries, 'delete': delete_entries }
    def produceSqlsByS3(self, s3) :
        if s3['nums'] == 0 : return list()

        sqls = { 'insert' : list(), 'update' : list(), 'delete' : list() }
        
        db_table = self.config[CFGNAME_DB_TABLE_PM]

        for entry in s3['insert']:
            sql = "insert into %s (`level`, `addr`, `label`, `parent_addr`, `children_addrs`) values ('%s',    '%s',    '%s'  , '%s'         , '%s')"  % (db_table, entry.level, entry.strAddr(), entry.label, entry.strParentAddr(), entry.strChildrenAddrs() )
            sqls['insert'].append(sql)
        
        for entry in s3['update']:
            sql = "update %s set( `label`='%s', `parent_addr`='%s', `children_addrs`='%s') where `addr`='%s' " % (db_table, entry.label, entry.strParentAddr(), entry.str_childre_addrs() , entry.strAddr() )
            sqls['update'].append(sql)

        for entry in s3['delete']: 
            sql = "delete from `%s` where `addr` = '%s'" % ( db_table, entry.strAddr() )
            sqls['delete'].append(sql)
    
        return sqls
    def commitSqls(self, sqls ):
        con = self.getConnection()
        cur = con.cursor()
        for sql_type in sqls:
            guard_sql_type = sql_type
            for sql in sqls[sql_type]:
                guard_sql = sql
                cur.execute( sql )
        return (True, sqls, None )
    
    ''' Functions sending requests to Machine '''

    def sendRequestsByS3( self, s3 ):
        for entry in s3['insert']:
            self.sendStartupRequest( entry )
        for entry in s3['update']:
            self.sendReconfigRequest( entry )
        for entry in s3['delete']:
            self.sendShutdownRequest( entry )

    def convnameType2Script(self, level):
        if level in ('cloud', 'Cloud') :
            return 'Cloud.py'
        elif level in ('cluster', 'Cluster'):
            return 'Cluster.py'
        elif level in ('rack', 'Rack'):
            return 'Rack.py'
        elif level in ('node', 'Node'):
            return 'Node.py'

    def sendStartupRequest(self, entry) :
    #''' ===== still have prombles I need to debug ===== '''
        print("Send request to {addr}".format( addr = entry.strAddr() ))

        script_dir = '/mnt/images/nfs/new_roystonea_script/roystonea_script/'
        script_file = self.convnameType2Script(entry.level)
        script_ab_file = script_dir + script_file
        log_ab_file = script_dir + "log/{host}-{port}-printout.txt".format(host=entry.host, port=entry.port);
        ssh_cmd = "nohup python {script_absolute_filepath} {host} {port} console_off > {log_ab} &".format( script_absolute_filepath = script_ab_file, host=entry.host, port=entry.port, log_ab=log_ab_file )
 
        print( ssh_cmd)

        account = 'ot32em'
        passwd = ''
        remote = pxssh.pxssh()
        t = remote.login( entry.host, account, passwd )
        print("Login done")
        remote.sendline( ssh_cmd )
        remote.prompt()
        remote.logout()
    
        print("Update the PM Relation to {host}:{port}.".format(host=entry.host, port=entry.port) )
        entry.dump_pretty()
        req = Message.CmdUpdatePMRelationReq(pm_relation=entry)
        res = Client.send_message( entry.addr, req )

    def sendReconfigRequest(self, entry) :    # reconfig
        cmdreq = Message.CmdSetPMRelationReq(pm_relation=entry)
        cmdres = Client.send_object( entry.addr, cmdreq )

    def sendShutdownRequest(self, entry) :  
        cmdreq = Message.CmdShutdownReq(after_secs=0)
        cmdres = Client.send_object( entry.addr, cmdreq )

    def demo(self):
        pass

if __name__ == '__main__' :
    host = 'localhost'
    port = 3000
    pmh = PM_Handler( host, port )
    
    newcol = pmh.getColByXml('relation_xmls/Relation_Exp.xml')
   # print("newcol: ")
    #print( newcol )
    s3 = pmh.produceS3ByCol( newcol )
    #print("s3:")
    #print(s3)
    sqls = pmh.produceSqlsByS3( s3 )
   # print("sqls:")
   # print( sqls )
    raw_input('ready to send all requests')
    pmh.sendRequestsByS3( s3 )
    pmh.dumpCol()

    
