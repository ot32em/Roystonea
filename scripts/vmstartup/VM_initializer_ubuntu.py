from VM_initializer import VM_initializer
from VM_ubuntu_cfg import *
import string
import pexpect
import sys
from template import template

class VM_initializer_ubuntu(VM_initializer):
				# 		  23,   r99944038,   4,    1,4096,  250,   4, roystonea03
    def __init__(self, vm_id, owner, group_num, vm_num, memory, disk_size, num_cpu, hostmachine):
        super(VM_initializer_ubuntu, self).__init__(vm_id, owner, group_num, vm_num, memory, disk_size, num_cpu, hostmachine)
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
        # config_path = self.vm_path+self.vm_name+'.xml'
        self.config_xml = template('ubuntu.xml.mustache', values)

    def start(self):
        self.creatDirectories()
        self.creatConfig()
        self.resizeImage()
        self.creatVM()

    def shutdown(self):
        self.shutdownVM()

def test(command):
    test = VM_initializer_ubuntu(97, 'illegalkao', 97, 97, 512, 10, 1, 'roystonea03')
    vm_ubuntu_method = getattr(test, command)
    print command
    print vm_ubuntu_method
    vm_ubuntu_method()

if __name__ == "__main__":
    test()
