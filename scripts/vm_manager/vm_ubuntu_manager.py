import string
import pexpect

from vm_manager_base import VMManagerBase
from etc.vm_manager.ubuntu import *
from template import template

class VMUbuntuManager(VMManagerBase):
				# 		  23,   r99944038,   4,    1,4096,  250,   4, roystonea03
    def __init__(self, vm_id, owner, group_num, vm_num, memory, disk_size, num_cpu, hostmachine):
        super(VMUbuntuManager, self).__init__(vm_id, owner, group_num, vm_num, memory, disk_size, num_cpu, hostmachine)
        self.image_name = IMAGE_NAME
        self.vm_name = owner + '-' + str(group_num) + '-' + str(vm_num)
        self.vm_path = PATH_SHARE_FILESYSTEM + owner + '/' + self.vm_name + '/'

    def creatDirectories(self):
        pexpect.run('mkdir ' + PATH_SHARE_FILESYSTEM + self.owner)
        pexpect.run('mkdir '+ self.vm_path)
        print(pexpect.run('cp '+ PATH_PROTOTYPE_IMAGE + self.vm_path))

    def creatConfig(self):
        values = {
                'memory'     : str(self.memory * 1024),
                'num_cpu'    : str(self.num_cpu),
                'name'       : self.vm_name,
                'image_path' : self.vm_path + self.image_name
                }

        config_path = self.vm_path+self.vm_name+'.cfg'
        template('ubuntu_xen.mustache', config_path, values)
        # self.config_xml = template('ubuntu.xml.mustache', values)

    def start(self):
        self.creatDirectories()
        self.creatConfig()
        self.resizeImage()
        self.creatVM()

    def shutdown(self):
        self.shutdownVM()

def test(command):
    test = VMUbuntuManager(1, 'royuser', 1, 1, 512, 10, 1, 'roystonea03')
    vm_ubuntu_method = getattr(test, command)
    vm_ubuntu_method()

if __name__ == "__main__":
    test()
