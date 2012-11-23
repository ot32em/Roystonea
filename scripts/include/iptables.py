import pexpect
import re
import threading
import socket


class iptable():
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

    def get_vmaddrs_by_hostport( hostport ):
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

