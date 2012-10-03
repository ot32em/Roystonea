from VM_initializer import VM_initializer
import pxssh
import logging
import string
import pexpect

class VM_initializer_hbase(VM_initializer):
    def __init__(self, vm_id, owner, group_num, vm_num, memory, disk_size, num_cpu, hostmachine):
        super(VM_initializer_hbase, self).__init__(vm_id, owner, group_num, vm_num, memory, disk_size, num_cpu, hostmachine)
        
        self.logger = logging.getLogger('roystonea.start.vm.hbase')
        self.image_name = 'gentoo.img'
        self.vm_name = owner+'-'+str(group_num)+'-'+str(vm_num)
        self.group_path = owner + '/' + owner + '-' + str(group_num)
        self.vm_path = '/var/SFS/hbase/' + self.group_path + '/' + self.vm_name + '/'
 
    def creatDirectories(self):
        self.logger.info('mkdir /var/SFS/hbase/'+ self.owner)
        pexpect.run('mkdir /var/SFS/hbase/'+ self.owner)

        self.logger.info('mkdir /var/SFS/hbase/'+ self.group_num)
        pexpect.run('mkdir /var/SFS/hbase/'+ self.group_num)

        self.logger.info('mkdir '+ self.vm_path)
        remote.sendline('mkdir' + self.vm_path)
        remote.prompt()

    def creatFstabFile(self):
        self.logger.info('sudo cp -p /mnt/images/nfs/vm_prototype/hadoop.2.6.38-rc4.hbase/slaves/fstab /var/SFS/hbase/' + self.group_path+ '/fstab')
        child3 = pexpect.spawn('sudo cp -p /mnt/images/nfs/vm_prototype/hadoop.2.6.38-rc4.hbase/slaves/fstab /var/SFS/hbase/' + self.group_path+ '/fstab')
        child3.expect(pexpect.EOF)

        file_fstab = open('/var/SFS/hbase/'+ self.group_path + '/fstab', 'a')
        if file_fstab:
            file_fstab.writelines(self.vm_name + ':/opt/apachehadoop /opt/apachehadoop   nfs v3  0   2')
            file_fstab.close()
            return True
        else:
            self.logger.info('Generating fstab file error.')
            return False

    def mountImage(self):
        if self.vm_num == 1:
            self.logger.info('cp /mnt/images/nfs/vm_prototype/hadoop.2.6.38-rc4.hbase/master/* '+ vm_path)
            self.remote.sendline('cp /mnt/images/nfs/vm_prototype/hadoop.2.6.38-rc4.hbase/master/* '+ vm_path)
            self.remote.prompt()
        else:
            self.logger.info('cp /mnt/images/nfs/vm_prototype/hadoop.2.6.38-rc4.hbase/slaves/* '+ vm_path)
            self.remote.sendline('cp /mnt/images/nfs/vm_prototype/hadoop.2.6.38-rc4.hbase/slaves/* '+ vm_path)
            self.remote.prompt()
        
            self.logger.info('sudo mount -o loop -t ext4 ' + vm_path + self.image_name + ' /mnt/floppy/')
            self.remote.sendline('sudo mount -o loop -t ext4 ' + vm_path + self.image_name + ' /mnt/floppy/')
            self.remote.prompt()

            self.logger.info('sudo cp -p /var/SFS/hbase/' + self.group_path + '/fstab /mnt/floppt/etc/')
            self.remote.sendline('sudo cp -p /var/SFS/hbase/' + self.group_path + '/fstab /mnt/floppt/etc/')
            self.remote.prompt()

            self.logger.info('sudo umount /mnt/floppt/')
            self.remote.sendline('sudo umount /mnt/floppt/')
            self.remote.prompt()
            
    def creatConfig(self)
        self.logger.info('Generating config......')
        config_path = self.vm_path + self.vm_name + '.cfg'
        config = open(config_path, 'w')
        if config:
            config.writelines('kernel = "/mnt/images/nfs/kernel/vmlinuz-2.6.38-rc4-domu"\n')
            config.writelines('memory = ' + str(self.memory) + '\n')
            config.writelines('vcpus = ' + str(self.num_cpu) + '\n')
            config.writelines("vif = [ '' ]\n")
            config.writelines('extra = "root=/dev/xvda1 ro console=hvc0 ip=::::'+self.vm_name+'::dhcp"\n')
            config.writelines('name = "'+str(self.vm_id)+'"\n')
            config.writelines("disk=['tap:aio:"+self.vm_path+self.image_name+",xvda1,w']\n")
            config.close()
        else:
            self.logger.error('Cannot generate config !!')
            return


    def remoteConnection(self):
        self.remote.login(self.hostmachine, self.account_name, '')


    def start(self):
        self.logger.info('Starting...')
        self.logger.info('VMname = '+self.vm_name+', VMid = '+str(self.vm_id)+', VirtualCpu = '+str(self.num_cpu)+', Memory = '+str(self.memory)+'mb,\
                 DiskSize = '+str(self.disk_size)+'G, HostMachine = '+self.hostmachine)
        self.remoteConnection()
        self.creatDirectories()
        
        if vm_num == 1:
            if not self.creatFstabFile():
                return
        
        self.mountImage()
        self.creatConfig()
        self.resizeImage()
        self.creatVM()
