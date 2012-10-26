from vm_manager_base import VMManagerBase
import string
import pexpect
from ubuntu import *

class VMApacheManager(VMManagerBase):
    def __init__(self, vm_id, owner, group_num, vm_num, memory, disk_size, num_cpu, hostmachine):
        super(VMApacheManager, self).__init__(vm_id, owner, group_num, vm_num, memory, disk_size, num_cpu, hostmachine)

        self.image_name = IMAGE_NAME
        self.vm_name = owner+'-'+str(group_num)+'-'+str(vm_num)
        self.vm_path = PATH_SHARE_FILESYSTEM + owner + '/' + self.vm_name + '/'

    def creatDirectories(self):
        pexpect.run('mkdir '+ PATH_SHARE_FILESYSTEM + self.owner)
        pexpect.run('mkdir '+ self.vm_path)
        temp=pexpect.run('cp ' + PATH_PROTOTYPE_IMAGE + self.vm_path)
        print(temp)

    def creatConfig(self):
        values = {
                'name'       : self.vm_name,
                'kernel'     : PATH_DOMU_KERNEL,
                'memory'     : str(self.memory * 1024),
                'num_cpu'    : str(self.num_cpu),
                'image_path' : self.vm_path + self.image_name
                }

        self.config_xml = template('apache.xml.mustache', values)

    def start(self):
        self.creatDirectories()
        self.creatConfig()
        self.resizeImage()
        self.creatVM()

    def shutdown(self):
        self.shutdownVM()

def test(command):
    test = VMApacheManager(95, 'illegalkao', 95, 95, 512, 20, 1, 'roystonea03')
    vm_apache_method = getattr(test, command)
    vm_apache_method()

if __name__ == "__main__":
    test()
