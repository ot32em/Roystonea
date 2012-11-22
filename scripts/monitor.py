'''
This is SubsystemManager.py
Remember to type "HOST" and "PORT" arguments when execute SubsystemManager.py
ex. "python Base.py 192.168.15.1 10000"

Note:
(1) You have to convert "HOST" to "int" type
(2) Must crate config file "subsystem_manager_cfg", you can reference other config files

by Teddy, 2012/02/17
'''

import os
import re
import time
import pexpect
from include.base_server import BaseServer
from include.hierachy import Hierachy
from include import message
from rootpath import ROYSTONEA_ROOT

class Monitor(BaseServer):
    ''' custom init variable '''
    level = 'Monitor'

    def __init__(self, host, port):
        super(Monitor, self).__init__(host, port)

        self.vmInfos = dict() # vmid as key, info as value
        self.daemonInfos = dict() # name as key, info as value
        self.pmInfos = dict() # hostname as key, info as value

        self.monitor_timeval = 10

        self.hierachy = Hierachy()

        self.register_start_function( self.PollingMonitorResource )

    def register_handle_functions(self):
        self.register_handle_function("MonitorAskNodeResourceListReq", self.askNodeResourceListHandler)
        self.register_handle_function("MonitorAskRackResourceListReq", self.askRackResourceListHandler)
        self.register_handle_function("MonitorAskClusterResourceListReq", self.askClusterResourceListHandler)

    def askNodeResourceListHandler(self, msg, client_addr=None ):
        rack_addr = msg.rack_addr
        
        rack_unit = self.hierachy.getDaemonByAddress( rack_addr )
        node_resource_list = rack_unit.children
        return node_resource_list
        
    def askRackResourceListHandler(self, msg, client_addr=None ):
        cluster_addr = msg.cluster_addr
        cluster_unit = self.hierachy.getDaemonByAddress( cluster_addr )

        rack_resource_list  = cluster_unit.children
        return rack_resource_list

    def askClusterResourceListHandler(self, msg, client_addr=None ):
        cloud_addr = msg.cloud_addr
        cloud_unit = self.hierachy.getDaemonByAddress( cloud_addr )
        rack_resource_list = cloud_unit.children
        
        return rack_resource_list

    def PollingMonitorResource(self):
        nodes = self.hierachy.getDaemonsByTypename("Node")
        machine_list= list()
        for name in nodes:
            machine_list.append( nodes[ name ].hostmachine )
        while 1:
            self.monitor( machine_list )
            time.sleep( self.monitor_timeval)

    
    def monitor( self, machine_list):
        # init memory info slot for each machine
        machine_resource_list = list()
        total_vm_status_list = list()

        for i in xrange( len(machine_list) ):
            machine_addr = machine_list[i] 
            machine_resource = dict()
            machine_resource["addr"] = machine_addr

            # vm_status info
            mixed_info = self.get_machine_memory_info_and_vm_status_list( machine_addr )
            vm_status_list = mixed_info['vm_status_list']
            total_vm_status_list = total_vm_status_list + vm_status_list

            # memory remaining info
            preserve_1G = 1 * 1024 * 1024
            remaining_memory = mixed_info['total_memory'] - mixed_info['used_memory'] - preserve_1G
            machine_resource['remaining_memory'] = remaining_memory

            # disk remaining info
            disk_info = self.get_machine_disk_info( machine_addr )
            machine_resource['remaining_disk'] = disk_info['remaining_disk'] 
            machine_resource['used_disk'] = disk_info['used_disk'] 
            machine_resource_list.append( machine_resource )


        self.notify_db_update_all_monitor_result( total_vm_status_list, machine_resource_list )
        self.update_hierachy_all_monitor_result( machine_resource_list )

    def notify_db_update_all_monitor_result( self, total_vm_status_list,  machine_resource_list ):
        print("monitor@notify_db called")
        addr = self.coordinator_addr
        msg_values = [ total_vm_status_list, machine_resource_list]
        msg = self.create_message( message.CoordinatorUpdateMonitorResultReq, msg_values )
        self.send_message( addr, msg )

    def update_hierachy_all_monitor_result( self, machine_resource_list ):
        nodeunit_list = self.hierachy.getDaemonsByTypename("Node")
        for nodename in nodeunit_list :
            nodeunit = nodeunit_list[nodename]
            for machine_resource in machine_resource_list :
                if machine_resource.addr == nodeunit.addr() :
                    nodeunit.set_memory( int( machine_resource['remaining_memory']) )
                    nodeunit.set_disk( int( machine_resource['remaining_disk']) )
                    nodeunit.set_used_disk( int( machine_resource['used_disk']) )


    def get_machine_memory_info_and_vm_status_list( self, machine_addr):
        result = dict()
        result['total_memory'] = self.get_machine_total_memory( machine_addr )
        tmp = self.get_machine_used_memory_and_vm_status_list( machine_addr )
        result['used_memory'] = tmp['used_memory']
        result['vm_status_list'] = tmp['vm_status_list']
        return result

    def get_machine_total_memory( self, machine_addr ):

        return 24*1024*1024 # 24 GB
        # following code detect dom0's max memory, so it's a wrong code 
        # not the whole memory xen can use
        space_pattern = re.compile("\s+")
        # see capacity memory 
        lessMeminfoCommand = "ssh {_machine_addr} less {meminfoFile}".format(
                _machine_addr = machine_addr, meminfoFile = "/proc/meminfo")
        print( lessMeminfoCommand )
        resultLines = pexpect.run( lessMeminfoCommand ).strip().split("\n")
        targetLinePattern = re.compile("^MemTotal:")

        memoryTotal = 0
        for line in resultLines :
            if targetLinePattern.match( line ):
                columns = space_pattern.split( line ) # line will like "MemTotal:     452454543 kB"
                memoryTotal = int( columns[1] )
                break
        return memoryTotal

    def get_machine_used_memory_and_vm_status_list( self, machine_addr ):
        xen_vm_name_prefix = "vm"
        xen_vm_name_pattern = re.compile( xen_vm_name_prefix + "\d+" ) # ex: vm123445
        space_pattern = re.compile( "\s+" )

        used_memory = 0
        vm_status_list = list()
        # command "xentop -i 2 -d 0.1 -b " output:
        #   NAME     STATE     CPU(sec) CPU(%)     MEM(k) MEM(%)  MAXMEM(k) MAXMEM(%)
        #   Domain-0 -----r     232891    0.0    2091520    8.3   no limit       n/a
        #   vm2057   --b---         54    0.0     262144    1.0     262144       1.0
        #   vm2113   --b---         54    0.0     262144    1.0     262144       1.0
        #   vm2132   --b---         56    0.0     262144    1.0     262144       1.0 
        #   NAME     STATE     CPU(sec) CPU(%)     MEM(k) MEM(%)  MAXMEM(k) MAXMEM(%)
        #   Domain-0 -----r     232891  127.3    2091520    8.3   no limit       n/a    
        #   vm2057   --b---         54    0.0     262144    1.0     262144       1.0    
        #   vm2113   --b---         54    0.0     262144    1.0     262144       1.0    
        #   vm2132   --b---         56    0.2     262144    1.0     262144       1.0    

        # counting avaliable memory 
        xentopCommand = "ssh {_machine_addr} sudo xentop -i 2 -d 0.1 -b".format( _machine_addr = machine_addr )
        resultLines = pexpect.run( xentopCommand).strip().split("\n")
        resultLines = resultLines[ (len( resultLines ) / 2) : ] # need strings[middleline~end]

        for line in resultLines :
            columns = space_pattern.split( line.strip() )
            if not columns :
                continue
            if columns[0] == "Domain-0":
                # hyperviser resource consume
                used_memory =  used_memory + int(columns[4])
            elif xen_vm_name_pattern.match( columns[0] ) :
                used_memory =  used_memory + int(columns[4])
                vm = { "vmid" : columns[0][len(xen_vm_name_prefix):], # vm1234 -> 1234
                       "hostmachine" : machine_addr,
                       "cpu_usage" : float( columns[3] ),
                       "used_memory" : int( columns[4]), 
                       "memory_usage" : float( columns[5]) }
                vm_status_list.append(vm)
        result = dict()
        result['used_memory'] = used_memory
        result['vm_status_list'] = vm_status_list
        return result

    def get_machine_disk_info( self, machine_addr):
        space_pattern = re.compile( "\s+" )
        # command "df /mnt/images/sfs" output:
        # Filesystem           1K-blocks      Used Available Use% Mounted on
        # /dev/mapper/vg-sfs   825698728 101306472 682449216  13% /mnt/images/sfs
        dfCommand = "ssh {_machine_addr} df {shareFileSystemPath}".format(
            _machine_addr = machine_addr, shareFileSystemPath = "/mnt/images/sfs" )

        resultLines = pexpect.run(dfCommand).strip().split("\n")
        columns = space_pattern.split( resultLines[1]) # discard first title line

        result = dict()
        result['remaining_disk'] = int( columns[3] )
        result['used_disk'] = float( columns[4][:-1] )
        return result

    def update_machine_resource( self, hostmachine, remaining_memory_KB, remaining_disk_KB, used_disk_percent) :
        print(" hostmachine: %s, remain-mem: %s, remain-disk: %s, usedDisk%%: %s " 
            % (hostmachine, remaining_memory_KB, remaining_disk_KB, used_disk_percent ) )
        return
        req = Message.UpdateHostMachineResourceReq( hostmachine = hostmachine,
                                                    remaining_memory_KB =remaining_memory_KB,
                                                    remaining_disk_KB = remaining_disk_KB,
                                                    used_disk_percent = used_disk_percent )
        coordinator = self.hierachy.getCoordinatorDaemon()
        Client.sendonly_message( (coordinator.host, coordinator.post), req )

    def update_vm_status_list( self, vm_list ):
        for vm in vm_list :
            print(" vm(%s), at %s, current cpu usage: %s, memory usage: %s " 
                % (vm['vmid'], vm['hostmachine'], vm['cpuUsage'], vm['memoryUsage'] ) )
        return
        
        req = Message.CoordinatorUpdateVmStatusListReq( vm_status_list = vm_list)
        coordinator = self.hierachy.getCoordinatorDaemon()
        Client.sendonly_message( coordinator.addr() , req )


def start(port):
    server = Monitor("127.0.0.1", port)
    server.run()


if __name__ == '__main__':
     Monitor.cmd_start()

