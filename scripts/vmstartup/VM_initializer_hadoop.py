from VM_initializer import VM_initializer
import string
import pexpect
from VM_ubuntu_cfg import *

class VM_initializer_hadoop(VM_initializer):
    def __init__(self, vm_id, owner, group_num, vm_num, memory, disk_size, num_cpu, hostmachine):
        super(VM_initializer_ubuntu, self).__init__(vm_id, owner, group_num, vm_num, memory, disk_size, hostmachine)
        self.image_name = IMAGE_NAME
        self.vm_name = owner+'-'+str(group_num)+'-'+str(vm_num)
        self.group_path = owner+'/'+owner+'-'+str(group_num)
        self.vm_path = PATH_SHARE_FILESYSTEM + self.group_path + '/' + self.vm_name + '/'

    def creatDirectories(self)
        pexpect.run('mkdir ' + PATH_SHARE_FILESYSTEM + self.owner)
        pexpect.run('mkdir ' + PATH_SHARE_FILESYSTEM + self.grouppath)
        pexpect.run('mkdir ' + self.vm_path)

        if self.vm_num == 1:
            pexpect.run('sudo cp -p ' + PATH_SLAVE_PROTOTYPE + FILE_FSTAB + ' ' + PATH_SHARE_FILESYSTEM + self.group_path + '/' + FILE_FSTAB)
            pexpect.run('cp ' + PATH_MASTER_PROTOTYPE + ' ' + self.vm_path)

            fstab = open(PATH_SHARE_FILESYSTEM + self.group_path + '/' + FILE_FSTAB, 'a')

            if fstab:
                fstab.writelines(self.vm_name+FSTAB_CONFIG)
                fstab.close()
            else:
                print('fstab file error.')
                return
        else:
            pexpect.run('cp ' + PATH_SLAVE_PROTOTYPE + 'gentoo.img ' + self.vm_path)
            pexpect.run('cp ' + PATH_SLAVE_PROTOTYPE + 'fstab ' + self.vm_path)
            pexpect.run('sudo mount -o loop -t ext4 '+ self.vm_path + self.image_name + ' ' + PATH_MOUNTPOINT)
            pexpect.run('sudo cp -p ' + PATH_SHARE_FILESYSTEM + self.group_path + '/' + FILE_FSTAB + ' ' + PATH_MOUNTPOINT)
            pexpect.run('sudo umount ' + PATH_MOUNTPOINT)
