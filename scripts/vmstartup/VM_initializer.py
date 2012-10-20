import pexpect
import string
import libvirt
import sys
import os
from VM_default_cfg import *

# TODO this code is only for test perpose
ROYSTONEA_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")
sys.path.append(ROYSTONEA_ROOT)
from logger import logger

class VM_initializer(object):
    account_name = LOGGING_ACCOUNT
    logger       = None
    remote       = None
    vm_path      = None
    image_name   = None
    config_path  = None
    vm_name      = None
    config_xml   = None
    conn         = None
    domain       = None

    def __init__(self, vm_id, owner, group_num, vm_num, memory, disk_size, num_cpu, hostmachine):
        self.vm_id = vm_id
        self.owner = owner
        self.group_num = group_num
        self.vm_num = vm_num
        self.memory = memory
        self.disk_size = disk_size
        self.num_cpu = num_cpu
        self.hostmachine = hostmachine
        self.conn = libvirt.open(None)
        if self.conn == None:
            logger.error("Hypervisor connection fail!")
            sys.exit(1)

    def resizeImage(self):
        print(pexpect.run(CMD_DISK_DUPLICATION + 'if=/dev/zero bs=1024k count=1 seek=' + str(self.disk_size) + 'k of=' + self.vm_path + self.image_name))
        print(pexpect.run(CMD_FILESYSTEM_CHK + self.vm_path + self.image_name))
        print(pexpect.run(CMD_RESIZE_FILESYSTEM + self.vm_path + self.image_name))

    def creatVM(self):
        # print pexpect.run(CMD_XEN_CREAT_VM + self.vm_path + self.vm_name+'.cfg')
        try:
            self.domain = self.conn.createXML(self.config_xml, 0)
        except:
            logger.error("VM creation fail!")

    def shutdownVM(self):
        # print pexpect.run(CMD_XEN_SHUTDOWN_VM + self.vm_name)
        domain = self.getDomain()
        if not domain: 
            return

        if self.conn.shutdown(domain) < 0:
            logger.error("VM %(name)s shutdown fail!" % ({'name': self.vm_name}))

    def getDomain():
        if self.domain == None:
            try:
                self.domain = self.conn.lookupByName(self.vm_name)
            except:
                logger.error("VM named %(name)s lookup fail!" % ({'name': self.vm_name}))

        return self.domain

    def listVM(self):
        print pexpect.run(CMD_XEN_LIST_VM)
