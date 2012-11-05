'''
This is Coordinator.py
Remember to type "HOST" and "PORT" arguments when execute Coordinator.py
ex. "python Coordinator.py 192.168.10.1 10000"

## You have to convert "HOST" to "int" type

by Teddy, 2012/03/07
'''

from include.CommonHandler import passArguments
from include.CommonHandler import CommonHandler
from include import Client, Message
from time import sleep
import time
import socket
import MySQLdb as mdb
import sys
from include.logger import logger
import pexpect


class Coordinator(CommonHandler):
    ''' custom init variable '''
    def __init__(self, host, port):
        self.FILENAME_MY_CONFIG = 'Coordinator_cfg.py'

        CommonHandler.__init__(self, host, port)
        self.dispatch_handlers.update({
            'RackAlgorithmResourceInformationReq': self.RackAlgorithmResourceInformation,
            'ClusterDatabaseSubsystemCreateVMres': self.ClusterDatabaseSubsystemCreateVM,
            'NodeDatabaseSubsystemAddPortReq': self.NodeDatabaseSubsystemAddPort,
        })
        self.startup_functions.extend((
            #self.databaseSubsystem,      
            self.CreateVmByCheckingDatabase,
            self.sayHello,          # hello function
        ))
        # database imformation, use config to replace this part
        self.db_host = self.config['db_host']
        self.db_account = self.config['db_account']
        self.db_password = self.config['db_password']
        self.db_name = self.config['db_name']

        self.cmd_iptables = self.config['cmd_iptables']

    
    def CreateVmByCheckingDatabase(self):
        timeval = 5
        vms = [ 
                { "vmid": 100, "groupid": 1, "vmsubid": 1, "ownerid": "1", "vmtype": "ubuntu", 
                    "config_cpu": "1", "config_memory": "1024", "config_disk": "40", "config_lifetime": "192" },
                { "vmid": 101, "groupid": 2, "vmsubid": 1, "ownerid": "1", "vmtype": "apache", 
                    "config_cpu": "2", "config_memory": "256", "config_disk": "20", "config_lifetime": "192" },
                { "vmid": 102, "groupid": 3, "vmsubid": 1, "ownerid": "1", "vmtype": "hadoop", 
                    "config_cpu": "3", "config_memory": "2048", "config_disk": "80", "config_lifetime": "192" },
                { "vmid": 103, "groupid": 3, "vmsubid": 2, "ownerid": "1", "vmtype": "hadoop", 
                    "config_cpu": "4", "config_memory": "2048", "config_disk": "80", "config_lifetime": "192" }
            ]

        vmseq = [ vms[0], None, None, vms[1], None, vms[2], vms[3]] # every 5 secs
        i = 0

        print("start detect in 3 secs")
        time.sleep(1)
        print("start detect in 2 secs")
        time.sleep(1)
        print("start detect in 1 secs")
        time.sleep(1)

        while 1 :
            if i < len(vmseq) :
                vm = vmseq[i]
                i = i + 1
                if vm != None :
                    print("detect new vm create from user!")
                    dir(vm)
                    req = Message.CreateVmByRackReq( vmid=vm['vmid'], groupid=vm['groupid'], vmsubid=vm['vmsubid'], ownerid=vm['ownerid'],
                                                  vmtype=vm['vmtype'], config_cpu=vm['config_cpu'], config_memory=vm['config_memory'], 
                                                  config_disk=vm['config_disk'], config_lifetime=vm['config_lifetime'])
                    destRackAddress = ("140.112.28.240", 7001)
                    Client.sendonly_message( destRackAddress, req )

            time.sleep(timeval)
        return
        db_host = "140.112.28.240"
        db_name = "roystonea_2012"
        db_user = "root"
        db_password = "87888"
        timeval = 5
        while 1:
            con = mdb.connect(db_host, db_user, db_password, db_name)
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute( 'SELECT * FROM vm WHERE vmstatus = "prepare_to_starts"a')
            
            rows = cur.fetchall()
            time.sleep(timeval)

   
    # receive msg from Rack to query imformation from database
    def RackAlgorithmResourceInformation(self, req):
        try:
            con = mdb.connect(self.db_host, self.db_account, self.db_password, self.db_name)
            
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute( 'SELECT * FROM resource WHERE rack = "%s"' %(req.rack) )
            
            rows = cur.fetchall()
            return rows

        except mdb.Error, e:
            print 'Error %d: %s' %(e.args[0], e.args[1])
            sys.exit(1)

        finally:
            if con:
                con.close()
    
    def ClusterDatabaseSubsystemCreateVM(self, req):
        try:
            con = mdb.connect(self.db_host, self.db_account, self.db_password, self.db_name)
            
            cur = con.cursor(mdb.cursors.DictCursor)
            
            if req.status == 'success':
                cur.execute( 'UPDATE vm SET state = "running" WHERE vm_id = "%s"' %(req.vm_id) )
            elif req.status == 'fail':
                cur.execute( 'UPDATE vm SET state = "start_fail" WHERE vm_id = "%s"' %(req.vm_id) )
            else:
                pass
            print 'OK!!!'

        except mdb.Error, e:
            print 'Error %d: %s' %(e.args[0], e.args[1])
            sys.exit(1)

        finally:
            if con:
                con.close()

    def NodeDatabaseSubsystemAddPort(self, req):
        try:
            con = mdb.connect(self.db_host, self.db_account, self.db_password, self.db_name)
            
            cur = con.cursor(mdb.cursors.DictCursor)
            add_port_query = 'INSERT INTO port (host_port, vm_port, vm_id, vm_name, owner, state, ip) \
                    VALUES (" ", "%s", "%s", %s, %s, "adding", " ")' %(req.vm_port, req.vm_id, req.vm_name, req.owner)
            cur.execute(add_port_query)
            
            return

        except mdb.Error, e:
            print 'Error %d: %s' %(e.args[0], e.args[1])
            sys.exit(1)

        finally:
            if con:
                con.close()

    # fetch quires from DB to create VM and send msg to Cluster
    def databaseSubsystem(self):
        try:
            con = mdb.connect(self.db_host, self.db_account, self.db_password, self.db_name)

            while True:
                cur = con.cursor(mdb.cursors.DictCursor)
                cur.execute('SELECT * FROM vm WHERE state = "prepare_to_start"')
                   
                rows = cur.fetchall()
                for row in rows:
                    try:
                        msg = Message.DatabaseSubsystemCreateVMreq(
                                vm_id = row['vm_id'],
                                group_num = row['group_num'],
                                vm_num = row['vm_num'],
                                vm_name = row['vm_name'],
                                owner = row['owner'],
                                type = row['type'],
                                cpu = row['cpu'],
                                mem = row['mem'],
                                disk = row['disk'],
                                )
                        
                        # use %s to not change data type
                        ###cur.execute( 'UPDATE vm SET state = "pending" WHERE vm_id = "%s"' %(row['vm_id']) )
                        
                        # Cluster's address
                        address = 'roystonea01', 9500
                        Client.sendonly_message(address, msg)
                        
                    except socket.error as e:
                        print 'socket error'
                        sleep(5)
                
                sleep(5)
        
        except mdb.Error, e:
            print 'Error %d: %s' %(e.args[0], e.args[1])
            sys.exit(1)
    
    def portmapping(self, vmname, vmip, vmport, hostport, action):
        if action == 'a':
            iptables_cmd = '%s %s PREROUTING -p tcp --dport %s -j DNAT --to %s:%s' \
                    %(self.cmd_iptables, '-A', hostport, vmip, vmport)
            logger.info('Add port mapping for %s, from %s to %s on hostmachine'%(vmname, vmport, hostport))
            logger.debug(iptables_cmd)

        elif action == 'd':
            iptables_cmd = '%s %s PREROUTING -p tcp --dport %s -j DNAT --to %s:%s' \
                    %(self.cmd_iptables, '-D', hostport, vmip, vmport)
            logger.info('Delete port mapping for %s, from %s to %s on hostmachine'%(vmname, vmport, hostport))
            logger.debug(iptables_cmd)
        else :
            logger.error('Error argument!')
            return 0

        (result, value) = pexpect.run(iptables_cmd, withexitstatus = 1)

        if value != 0 :
            logger.error(result)
            return 0

        return 1

        if connect:
            logger.info('Start.')
            logger.info('Database connected.')
            while 1:
                query_portreq = "SELECT * FROM %s WHERE state='adding' \
                        OR state='deleting 'ORDER BY hostport"%(porttb)
                db.query(query_portreq)
                req_res = db.store_result()
                fetched_req_data = req_res.fetch_row()
                while fetched_req_data:
                    state = fetched_req_data[0][idx_state]
                    vmname = fetched_req_data[0][idx_vmname]
                    vmport = fetched_req_data[0][idx_vmport]
                    oldhostport = fetched_req_data[0][idx_hostport]

                    if (state == 'adding') :
                        vmip = socket.gethostbyname(vmname)
                        newport = oldhostport
                        if (newport == '-1') :
                            newport = get_port()
                        if (newport != -1) :
                            portmapping(vmname, vmip, vmport, newport, 'a')
                            query = "UPDATE %s SET state='using', \
                                hostport='%s', ip='%s' \
                                WHERE hostport=%s"%(porttb, newport, vmip, oldhostport)
                            db.query(query)
                        else :
                            logger.error('No more port!')
                    elif (fetched_req_data[0][idx_state] == 'deleting') :
                        #delete port
                        vmip = fetched_req_data[0][idx_ip]
                        portmapping(vmname, vmip, vmport, oldhostport, 'd')
                        query = "DELETE FROM %s WHERE hostport=%s"%(porttb, oldhostport)
                        db.query(query)
                    else :
                        logger.error("I don't know what's wrong!")

                fetched_req_data = req_res.fetch_row()
            time.sleep(sleep_time)
    def sayHello(self):
        print 'Hello'
    
if __name__ == '__main__':
    host, port, console_off = passArguments()
    mymachine = Coordinator( host, port )
    mymachine.run(console_off)

