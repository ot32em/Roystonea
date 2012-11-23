import time
import pexpect
from include.base_server import BaseServer
from include import message
from include.logger import logger

class Portmapping(BaseServer):
    ''' custom init variable '''
    num_rthreads = 4
    level = 'subsystem_manager'
    
    def __init__(self, host, port):
        super( Portmapping, self).__init__(host, port)

        self.hostport_lock = threading.Lock() # avoid geting duplicate hostport


    def register_handle_functions(self):
        self.register_handle_function("PortmappingAddPortmappingHandler", self.AddPortmappingHandler )
        self.register_handle_function("PortmappingDeletePortmappingHandler", self.DeletePortmappingHandler )


    def AddPortmappingHandler(self, msg, client_addr=None):
        hostport = self.get_unused_hostport()
        vmip = self.get_vmip( msg.vmname )
        vmport = msg.vmport

        self.add_portmapping(hostport, vmip, vmport)
        self.notify_db_added( hostport )

    def DeletePortmappingHandler(self, msg, client_addr=None):
        hostport = self.get_unused_hostport()
        vmip = self.get_vmip( msg.vmname )
        vmport = msg.vmport

        self.delete_portmapping(hostport, vmip, vmport)
        self.notify_db_deleted( hostport )

    def iptable_cmd(self):
        return "iptables -t nat -p tcp -j DNAT --to {vmip}:{vmport} --dport {hostport} {action}"

    def get_unused_hostport(self):
        with self.hostport_lock:
#            connect to coordinate to scan unused hostport

    def add_portmapping( self, hostport, vmip, guestport ):
        cmd = self.iptable_cmd().format( vmip=vmip, vmport=guestport, hostport=hostport, action="-A PREROUTING")
        pexpect.run( cmd )

    def delete_portmapping( self, hostport, vmip, guestport ):
        cmd = self.iptable_cmd().format( vmip=vmip, vmport=guestport, hostport=hostport, action="-D PREROUTING")
        pexpect.run( cmd )

    def notify_db_added( self, hostport ):
        addr = self.coordinator_addr
        msg_values = [hostport]
        msg = self.create_message( message.CoordinatorUpdatePortmappingAddedReq, msg_values)

    def notify_db_deleted( self, hostport ):
        addr = self.coordinator_addr
        msg_values = [hostport]
        msg = self.create_message( message.CoordinatorUpdatePortmappingDeletedReq, msg_values)




        
                                
        

    def get_vmip(self, vmname):
        try:
            return socket.gethostbyname( vmname )
        except socket.gaierror as e:
            return None

    


if __name__ == '__main__':
    host, port, console_off = passArguments()
    mymachine = SubsystemManager( host, port )
    mymachine.run(console_off)

