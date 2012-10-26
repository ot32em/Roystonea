from VM_initializer import VM_initializer
import string
import pexpect
from VM_apache_cfg import *

class VM_initializer_apache(VM_initializer):
    def __init__(self, vm_id, owner, group_num, vm_num, memory, disk_size, num_cpu, hostmachine):
        super(VM_initializer_apache, self).__init__(vm_id, owner, group_num, vm_num, memory, disk_size, num_cpu, hostmachine)

        self.image_name = IMAGE_NAME
        self.vm_name = owner+'-'+str(group_num)+'-'+str(vm_num)
        self.vm_path = PATH_SHARE_FILESYSTEM + owner + '/' + self.vm_name + '/'

    def creatDirectories(self):
        pexpect.run('mkdir '+ PATH_SHARE_FILESYSTEM + self.owner)
        pexpect.run('mkdir '+ self.vm_path)
        temp=pexpect.run('cp ' + PATH_PROTOTYPE_IMAGE + self.vm_path)
        print(temp)

    def creatConfig(self):
        config_path = self.vm_path+self.vm_name+'.cfg'
        config = open(config_path, 'w')
        if config:
            config.writelines("kernel = '"+ PATH_DOMU_KERNEL + "'\n")
            config.writelines('memory = ' + str(self.memory) + '\n')
            config.writelines('vcpus = ' + str(self.num_cpu) + '\n')
            config.writelines("vif = ['']\n")
            config.writelines('name = "'+str(self.vm_id)+'"\n')
            config.writelines("disk=['tap:aio:"+self.vm_path+self.image_name+",xvda1,w']\n")
            config.writelines('extra = "root=/dev/xvda1 ro console=hvc0 ip=::::'+ self.vm_name + '::dhcp"\n')
            config.close()

    def start(self):
        self.creatDirectories()
        self.creatConfig()
        self.resizeImage()
        self.creatVM()

if __name__ == "__main__":
     test = VM_initializer_apache(95, 'illegalkao', 95, 95, 512, 20, 1, 'roystonea03')
     test.start()
