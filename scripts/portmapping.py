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


    def SubsystemPortmappingTest(self):
        print 'hi this is portmapping'
        vmid = 472
        guestport = 22
        vmname = 'ot32em-8-8'
        portstatus = 'adding'
        hostport = 4000


        vmip = socket.gethostbyname(vmname)

        if portstatus == 'adding':
            # iptable -t nat -A PREROUTING -p tcp --dport $hostpot -j DNAT --to $intraIP:$guestport
            iptables_cmd = '%s %s PREROUTING -p tcp --dport %s -j DNAT --to %s:%s' \
                    %(self.config['cmd_iptables'], '-A', hostport, vmip, guestport)
            logger.info('Add port mapping for %s, from %s to %s on hostmachine'%(vmname, guestport, hostport)) 
        elif portstatus == 'deleting':
            # iptable -t nat -D PREROUTING -p tcp --dport $hostpot -j DNAT --to $intraIP:$guestport
            iptables_cmd = '%s %s PREROUTING -p tcp --dport %s -j DNAT --to %s:%s' \
                    %(cmd_iptables, '-D', hostport, vmip, guestport)
            logger.info('Delete port mapping for %s, from %s to %s on hostmachine'%(vmname, guestport, hostport)) 

        (result, value) = pexpect.run(iptables_cmd, withexitstatus = 1)
    
    def SubsystemPortMapping(self, req):
        portstatus = req.data[self.config['portstatus_index']]
        vmname = req.data[self.config['vmname_index']]
        guestport = req.data[self.config['guestport_index']]
        hostport = req.data[self.config['hostport_index']]

        vmip = socket.gethostbyname(vmname)

        if portstatus == 'adding':
            iptables_cmd = '%s %s PREROUTING -p tcp --dport %s -j DNAT --to %s:%s' \
                    %(self.config['cmd_iptables'], '-A', hostport, vmip, guestport)
            logger.info('Add port mapping for %s, from %s to %s on hostmachine'%(vmname, guestport, hostport)) 
        elif portstatus == 'deleting':
            iptables_cmd = '%s %s PREROUTING -p tcp --dport %s -j DNAT --to %s:%s' \
                    %(cmd_iptables, '-D', hostport, vmip, guestport)
            logger.info('Delete port mapping for %s, from %s to %s on hostmachine'%(vmname, guestport, hostport)) 

        (result, value) = pexpect.run(iptables_cmd, withexitstatus = 1)

    def add_portmapping( self, hostport, ip, guestport ):

    def get_vmip(self, vmname):
        try:
            return socket.gethostbyname( vmname )
        except socket.gaierror as e:
            return None

    


if __name__ == '__main__':
    host, port, console_off = passArguments()
    mymachine = SubsystemManager( host, port )
    mymachine.run(console_off)

