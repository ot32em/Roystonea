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
                'memory'     : str(self.memory),
                'num_cpu'    : str(self.num_cpu),
                'name'       : self.vm_name,
                'image_path' : self.vm_path + self.image_name
                }
        config_path = self.vm_path+self.vm_name+'.cfg'
        template('ubuntu_xen.mustache', config_path, values)

    def start(self):
        self.creatDirectories()
        self.creatConfig()
        self.resizeImage()
        self.creatVM()

    def shutdown(self):
        self.shutdownVM()

if __name__ == "__main__":
    test = VM_initializer_ubuntu(97, 'illegalkao', 97, 97, 512, 10, 1, 'roystonea03')
    command = sys.argv[1]
    vm_ubuntu_method = getattr(test, command)
    vm_ubuntu_method()
