import time
import pexpect
from include.base_server import BaseServer
from include import message
from include.logger import logger

class Portmapping(BaseServer):
    ''' custom init variable '''
    num_rthreads = 4
    level = 'subsystem_manager'

    self.iptable = Iptable()
    
    def __init__(self, host, port):
        super( Portmapping, self).__init__(host, port)

        self.hostport_lock = threading.Lock() # avoid geting duplicate hostport
        self.register_start_function(self.load_iptable )
        self.register_start_function(self.syncPortmapping)
    


    def register_handle_functions(self):
        self.register_handle_function("PortmappingAddPortmappingHandler", self.AddPortmappingHandler )
        self.register_handle_function("PortmappingDeletePortmappingHandler", self.DeletePortmappingHandler )

    def load_iptable(self):
        self.iptable.load()

    def AddPortmappingHandler(self, msg, client_addr=None):
        vmip = self.iptable.get_ip_by_name( msg.vmname )
        vmport = msg.vmport
        with self.iptable.lock:
            hostport = self.iptable.get_unused_hostport()
            self.iptable.add_portmapping(hostport, vmip, vmport)
        self.notify_db_added( hostport )

    def DeletePortmappingHandler(self, msg, client_addr=None):
        vmip = self.iptable.get_ip_by_name( msg.vmname )
        vmport = msg.vmport
        with self.iptable.lock():
            hostport = self.iptable.get_unused_hostport()
            self.iptable.delete_portmapping(hostport, vmip, vmport)
        self.notify_db_added( hostport )

    def syncPortmapping(self): # fix unsync data between daemon and db every 12 hrs
        timeval = 3600 * 12
        while True:
            time.sleep( timeval )
            self.iptable.load()

            db_hport_dict = get_portmapping_from_db()
            with self.iptable.lock:
                # db is more important
                for db_hport in db_hport_dict:
                    sys_vm_addr = self.iptable.get_vmaddr_by_hostport( db_hport )
                    if not sys_vm_addr : # port at db but not at system
                        db_vmip = db_hport[0]
                        db_vmport = db_hport[1]
                        self.iptable.add_portmapping( db_hport, db_vmip, db_vmport)
                    elif sys_vm_addr != db_hport_dict[db_hport] : # hostport missmatch
                        # change hostport of sys_vm_addr  to another
                        self.iptable.delete_portmapping( db_hostport, sys_vm_addr[0], sys_vm_addr[1])
                        new_sys_hostport = self.iptable.get_unused_hostport()
                        self.iptable.add_portmapping( new_sys_hostport, sys_vm_addr[0], sys_vm_addr[1])

                        # add hostport of db record
                        db_vmaddr = db_hport_dict[db_hport]
                        self.iptable.add_portmapping( db_hostport, db_vmaddr[0], db_vmaddr[1] )

    def get_portmapping_from_db(self ):
        msg = self.create_message(message.CoordinatorSelectAllPortmappingReq)
        data = self.send_message( self.coordinator_addr, msg )
        hport = dict() # hostport as key, (vmip, vmport) as value
        for row in data:
            hostport = row["hostport"]
            vmname = row["vmname"]
            vmport = row["vmport"]
            vmip = self.iptable.get_ip_by_hostname ( vmname )
            hport[ hostport ] = ( vmip, vmport )
        return hport



    def notify_db_added( self, hostport ):
        addr = self.coordinator_addr
        msg_values = [hostport]
        msg = self.create_message( message.CoordinatorUpdatePortmappingAddedReq, msg_values)

    def notify_db_deleted( self, hostport ):
        addr = self.coordinator_addr
        msg_values = [hostport]
        msg = self.create_message( message.CoordinatorUpdatePortmappingDeletedReq, msg_values)
    
class Iptable():
    def __init__(self):
        self.ip_dict = dict()
        self.hport_dict = dict()
        self.lock = threading.Lock()

    def load(self):
        result = pexpect.run("sudo iptables -t nat -S PREROUTING")
        re_nl = re.compile("\n")
        lines = re_nl.split( result )

        re_dest = re.compile("--to-destination\s\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}")
        subre_vmport = re.compile("\d{1,5}$")
        subre_vmip = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
        re_dport = re.compile("--dport \d{1,5}")
        subre_hostport = re.compile("\d{1,5}$")


        self.ip_dict = dict()
        self.hport_dict = dict()
        i = 1
        for line in lines :
            line = line.strip(" \t\n\r")

        find_dest = re_dest.findall(line)
        find_dport = re_dport.findall(line)
        if not find_dest or not find_dport :
            continue
        find_dest = find_dest[0]
        find_dport = find_dport[0]

        vmport = int(subre_vmport.findall( find_dest )[0] )
        vmip = subre_vmip.findall( find_dest )[0]

        hostport = int( subre_hostport.findall( find_dport )[0] )

        if not self.ip_dict.has_key( vmip ) :
            vmip_entry = { vmport: hostport }
            self.ip_dict[vmip] = vmip_entry
        else:
            self.ip_dict[vmip].update( {vmport: hostport} )

        self.hport_dict[ hostport ] = ( vmip, vmport )

    def get_ip_by_hostname(self, hostname):
        return socket.gethostbyname( hostname )

    def get_unused_hostport(self):
    # caution! implictly iccur  race condition
        try_times = 100
        port = max( self.hport.keys() ) + 1
        for i in xrange( try_times ):
            s = socket.socket( socket.AF_INET )
            try:
                s.bind( ("localhost", port) )
                s.close()
                return port
            except socket.error as e
                port = port + 1
                continue
    return port

    def get_ports_by_vmip(self, vmip):
        if self.ip_dict.had_key( vmip ) :
            return copy( self.ip_dict[vmip] )
        return dict()

    def get_vmaddr_by_hostport( hostport ):
        if self.hport.has_key( hostport ):
            return copy( self.hport[ hostport ] )
        return list()

    def iptable_cmd(self):
        return "sudo iptables -t nat -p tcp -j DNAT --to {vmip}%{vmport} --dport {hostport} {action}"

    def add_portmapping( hostport, vmip, vmport ):
        if hport.has_key( hostport ) :
            raise Exception("hostport duplicated")
        add_cmd = self.iptable_cmd().format( vmip=vmip, vmport=vmport, hostport=hostport,
                    action=" -A PREROUTING")
        pexpect.run( add_cmd )

        self.hport_dict[ hostport] = (vmip, vmport )
        if not ip_dict.has_key( vmip ) :
            self.ip_dict[vmip] = dict()
        self.ip_dict[vmip][vmport] = hostport


    def delete_portmapping( hostport, vmip, vmport ):
        if not hport.has_key( hostport ):
            raise Exception("Hostport %s does not exist." % hostport )
        add_cmd = self.iptable_cmd().format( vmip=vmip, vmport=vmport, hostport=hostport,
                    action=" -D PREROUTING")
        pexpect.run( add_cmd )

        del self.hport_dict[ hostport ]
        del self.ip_dict[vmip][vmport]
        if not self.ip_dict[vmip]:
            del self.ip_dict[vmip]


if __name__ == '__main__':
    host, port, console_off = passArguments()
    mymachine = SubsystemManager( host, port )
    mymachine.run(console_off)

