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
from include.CommonHandler import  passArguments, CommonHandler
from include.hierachy import Hierachy
from rootpath import ROYSTONEA_ROOT

class SubsystemManager(CommonHandler):
    ''' custom init variable '''
    num_rthreads = 4
    FILENAME_MY_CONFIG = 'subsystem_manager_cfg'
    level = 'subsystem_manager'
    
    def __init__(self, host, port):
        CommonHandler.__init__(self, host, port)
        self.dispatch_handlers.update({
            'NetworkingSubsystemPortMappingReq': self.NetworkingSubsystemPortMapping,
        })
        self.startup_functions.extend((
            self.MonitorResource,
            self.StorageSubsystem, # reclaiming space from files that are no longer used
            self.sayHello, # hello function              
        ))

        hierachyPath = os.path.join( ROYSTONEA_ROOT, "etc/Hierachy.xml")
        self.hierachy = Hierachy(hierachyPath)
   
    def NetworkingSubsystemPortMapping(self, req):
        pass
    
    def MonitorResource(self):
        pollingTimeval = 10 # 10secs update
        nodes = self.hierachy.getDaemonsByType("Node")
        machineList = list()
        for name in nodes:
            machineList.append( nodes[ name ].hostmachine )
        while 1:
            self.monitor( machineList )
            time.sleep( pollingTimeval )

    def MonitoringSubsystemVM(self):
        pass
    
    def StorageSubsystem(self):
        pass

    def sayHello(self):
        print 'Hello'
    
    def monitor( self, machineList ):
        # init memory info slot for each machine
        memoriesRemainingKB = [ None for i in xrange( len(machineList) ) ]
        disksRemainingKB = [ None for i in xrange( len(machineList) ) ]
        disksUsedPercent = [ None for i in xrange( len(machineList) ) ]

        for i in xrange( len(machineList) ):
            machineAddress = machineList[i] 

            # memory remaining info
            memoryInfo = self.getHostMachineMemoryInfoAndVmResourceInfo( machineAddress )
            vmResourceInfo = memoryInfo['VmResourceInfo']
            preserve1G = 1 * 1024 * 1024
            memoriesRemainingKB[i] = memoryInfo['Total'] - memoryInfo['Used'] - preserve1G

            # disk remaining info
            diskStatus = self.getHostMachineDiskInfo( machineAddress )
            disksRemainingKB[i] = diskStatus['Remaining'] 
            disksUsedPercent[i] = diskStatus['Used'] 

            self.updateHostMachineResource( hostmachine  = machineAddress,
                                       remainingMemory = memoriesRemainingKB[i],
                                       remainingDisk = disksRemainingKB[i],
                                       usedDiskPercent = disksUsedPercent[i] )
            self.updateManyVmResource( vmResourceInfo )

    def getHostMachineMemoryInfoAndVmResourceInfo( self,machineAddress ):
        result = dict()
        result['Total'] = self.getHostMachineTotalMemory( machineAddress )
        tmp = self.getHostMachineUsedMemoryAndManyVmResourceInfo( machineAddress )
        result['Used'] = tmp['Used']
        result['VmResourceInfo'] = tmp['VmResourceInfo']
        return result

    def getHostMachineTotalMemory( self,machineAddress ):

        return 24*1024*1024 # 24 GB
        # following code detect dom0's max memory, so it's a wrong code 
        # not the whole memory xen can use
        whitespacePattern = re.compile("\s+")
        # see capacity memory 
        lessMeminfoCommand = "ssh {_machineAddress} less {meminfoFile}".format(
                _machineAddress = machineAddress, meminfoFile = "/proc/meminfo")
        print( lessMeminfoCommand )
        resultLines = pexpect.run( lessMeminfoCommand ).strip().split("\n")
        targetLinePattern = re.compile("^MemTotal:")

        memoryTotal = 0
        for line in resultLines :
            if targetLinePattern.match( line ):
                columns = whitespacePattern.split( line ) # line will like "MemTotal:     452454543 kB"
                memoryTotal = int( columns[1] )
                break
        return memoryTotal

    def getHostMachineUsedMemoryAndManyVmResourceInfo( self, machineAddress ):
        xenVmNamePrefix = "vm"
        xenVmNamePattern = re.compile( xenVmNamePrefix + "\d+" ) # ex: vm123445
        whitespacePattern = re.compile( "\s+" )

        usedMemory = 0
        vms = list()
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
        xentopCommand = "ssh {_machineAddress} sudo xentop -i 2 -d 0.1 -b".format( _machineAddress = machineAddress )
        resultLines = pexpect.run( xentopCommand).strip().split("\n")
        resultLines = resultLines[ (len( resultLines ) / 2) : ] # need strings[middleline~end]

        for line in resultLines :
            columns = whitespacePattern.split( line.strip() )
            if not columns :
                continue
            if columns[0] == "Domain-0":
                # hyperviser resource consume
                usedMemory =  usedMemory + int(columns[4])
            elif xenVmNamePattern.match( columns[0] ) :
                usedMemory =  usedMemory + int(columns[4])
                vm = { "vmid" : columns[0][len(xenVmNamePrefix):], # vm1234 -> 1234
                       "hostmachine" : machineAddress,
                       "cpuUsage" : float( columns[3] ),
                       "memoryUsage" : float( columns[4]) }
                vms.append(vm)
        result = dict()
        result['Used'] = usedMemory
        result['VmResourceInfo'] = vms
        return result

    def getHostMachineDiskInfo( self, machineAddress):
        whitespacePattern = re.compile( "\s+" )
        # command "df /mnt/images/sfs" output:
        # Filesystem           1K-blocks      Used Available Use% Mounted on
        # /dev/mapper/vg-sfs   825698728 101306472 682449216  13% /mnt/images/sfs
        dfCommand = "ssh {_machineAddress} df {shareFileSystemPath}".format(
            _machineAddress = machineAddress, shareFileSystemPath = "/mnt/images/sfs" )

        resultLines = pexpect.run(dfCommand).strip().split("\n")
        columns = whitespacePattern.split( resultLines[1]) # discard first title line

        result = dict()
        result['Remaining'] = int( columns[3] )
        result['Used'] = float( columns[4][:-1] )
        return result

    def updateHostMachineResource( self, hostmachine, remainingMemory, remainingDisk, usedDiskPercent ) :
        print(" hostmachine: %s, remain-mem: %s, remain-disk: %s, usedDisk%%: %s " 
            % (hostmachine, remainingMemory, remainingDisk, usedDiskPercent ) )
        return
        req = Message.UpdateHostMachineResourceReq( hostmachine = hostmachine,
                                                    remainingMemory =remainingMemory,
                                                    remainingDisk = remainingDisk,
                                                    usedDiskPercent = usedDiskPercent )
        coordinator = self.hierachy.getCoordinatorDaemon()
        Client.sendonly_message( (coordinator.host, coordinator.post), req )

    def updateManyVmResource( self, vms ):
        for vm in vms :
            print(" vm(%s), at %s, current cpu usage: %s, memory usage: %s " 
                % (vm['vmid'], vm['hostmachine'], vm['cpuUsage'], vm['memoryUsage'] ) )
        return
        
        req = Message.UpdateManyVmsResourceReq( vmsResourceInfo = vms )
        coordinator = self.hierachy.getCoordinatorDaemon()
        Client.sendonly_message( (coordinator.host, coordinator.port ), req )


if __name__ == '__main__':
    host, port, console_off = passArguments()
    mymachine = SubsystemManager( host, port )
    mymachine.run(console_off)

