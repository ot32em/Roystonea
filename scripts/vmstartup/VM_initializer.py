import pexpect
import string
from VM_default_cfg import *

class VM_initializer(object):
    account_name = LOGGING_ACCOUNT
    logger = None
    remote = None
    vm_path = None
    image_name = None
    config_path = None
    vm_name = None

    def __init__(self, vm_id, owner, group_num, vm_num, memory, disk_size, num_cpu, hostmachine):
        self.vm_id = vm_id
        self.owner = owner
        self.group_num = group_num
        self.vm_num = vm_num
        self.memory = memory
        self.disk_size = disk_size
        self.num_cpu = num_cpu
        self.hostmachine = hostmachine

    def resizeImage(self):
        print(pexpect.run(CMD_DISK_DUPLICATION + 'if=/dev/zero bs=1024k count=1 seek=' + str(self.disk_size) + 'k of=' + self.vm_path + self.image_name))
        print(pexpect.run(CMD_FILESYSTEM_CHK + self.vm_path + self.image_name))
        print(pexpect.run(CMD_RESIZE_FILESYSTEM + self.vm_path + self.image_name))

    def creatVM(self):
        print pexpect.run(CMD_XEN_CREAT_VM + self.vm_path + self.vm_name+'.cfg')

    def shutdownVM(self):
        print pexpect.run(CMD_XEN_SHUTDOWN_VM + self.vm_name)

    def listVM(self):
        print pexpect.run(CMD_XEN_LIST_VM)
