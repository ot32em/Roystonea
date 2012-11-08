import pexpect
import re

def monitor( machineList ):
# init memory info slot for each machine
    memoriesRemainingKB = [ None for i in xrange( len(machineList) ) ]
    disksRemainingKB = [ None for i in xrange( len(machineList) ) ]
    disksUsedPercent = [ None for i in xrange( len(machineList) ) ]

    for i in xrange( len(machineList) ):
        machineAddress = machineList[i] 

        # memory remaining info
        memoryInfo = getHostMachineMemoryInfoAndVmResourceInfo( machineAddress )
        vmResourceInfo = memoryInfo['VmResourceInfo']
        preserve1G = 1 * 1024 * 1024
        memoriesRemainingKB[i] = memoryInfo['Total'] - memoryInfo['Used'] - preserve1G

        # disk remaining info
        diskStatus = getHostMachineDiskInfo( machineAddress )
        disksRemainingKB[i] = diskStatus['Remaining'] 
        disksUsedPercent[i] = diskStatus['Used'] 

        updateHostMachineResource( hostmachine  = machineAddress,
                                   remainingMemory = memoriesRemainingKB[i],
                                   remainingDisk = disksRemainingKB[i],
                                   usedDiskPercent = disksUsedPercent[i] )
        updateManyVmResource( vmResourceInfo )

def getHostMachineMemoryInfoAndVmResourceInfo( machineAddress ):
    result = dict()
    result['Total'] = getHostMachineTotalMemory( machineAddress )
    tmp = getHostMachineUsedMemoryAndManyVmResourceInfo( machineAddress )
    result['Used'] = tmp['Used']
    result['VmResourceInfo'] = tmp['VmResourceInfo']
    return result

def getHostMachineTotalMemory(machineAddress ):
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

def getHostMachineUsedMemoryAndManyVmResourceInfo( machineAddress ):
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

def getHostMachineDiskInfo(machineAddress):
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

def updateHostMachineResource( hostmachine, remainingMemory, remainingDisk, usedDiskPercent ) :
    print(" hostmachine: %s, remain-mem: %s, remain-disk: %s, usedDisk%%: %s " 
        % (hostmachine, remainingMemory, remainingDisk, usedDiskPercent ) )

def updateManyVmResource( vms ):
    for vm in vms :
        print(" vm(%s), at %s, current cpu usage: %s, memory usage: %s " 
            % (vm['vmid'], vm['hostmachine'], vm['cpuUsage'], vm['memoryUsage'] ) )


if __name__ == '__main__':
    hostmachineList = [ 
                    "roystonea01",
                    "roystonea02",
                    "roystonea03",
    ]
    monitor( hostmachineList )
