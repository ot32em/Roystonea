'''
This is Coordinator.py
Remember to type "HOST" and "PORT" arguments when execute Coordinator.py
ex. "python Coordinator.py 192.168.10.1 10000"

## You have to convert "HOST" to "int" type

by Teddy, 2012/03/07

from scripts.include.CommonHandler import  passArguments
from scripts.include.Client import *
from time import sleep
import socket

import MySQLdb as mdb
import sys
from scripts.include import CommonHandler, Message

'''
#from Roystonea.logger import logger
# import os
from logger import logger
#TODO import pexpect

class Coordinator(CommonHandler):
    from config.coordinatorConfig import *
    ''' custom init variable '''
    FILENAME_MY_CONFIG = FILENAME_MY_CONFIG
    num_rthreads = num_rthreads
    level = level
    
    def __init__(self, host, port):
        CommonHandler.__init__(self, host, port)
        self.dispatch_handlers.update({
            'RackAlgorithmResourceInformationReq': self.RackAlgorithmResourceInformation,
            'ClusterDatabaseSubsystemCreateVMres': self.ClusterDatabaseSubsystemCreateVM,
            'NodeDatabaseSubsystemAddPortReq': self.NodeDatabaseSubsystemAddPort,
        })
        self.startup_functions.extend((
            self.databaseSubsystem,      
            self.sayHello,          # hello function
        ))
        # database imformation, use config to replace this part
        self.db_host = db_host
        self.db_account = db_account
        self.db_password = db_password
        self.db_name = db_name
   
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
                        sendonly_message(address, msg)
                        
                    except socket.error as e:
                        print 'socket error'
                        sleep(5)
                
                sleep(5)
        
        except mdb.Error, e:
            print 'Error %d: %s' %(e.args[0], e.args[1])
            sys.exit(1)
    
    def PortMapping(self, vmname, vmip, vmport, hostport, action):
        if action == 'a':
            #TODO cmd_iptables
            iptables_cmd = '%s %s PREROUTING -p tcp --dport %s -j DNAT --to %s:%s' \
                    %(cmd_iptables, '-A', hostport, vmip, vmport)
            logger.info('Add port mapping for %s, from %s to %s on hostmachine'%(vmname, vmport, hostport))
            logger.debug(iptables_cmd)

        elif action == 'd':
            iptables_cmd = '%s %s PREROUTING -p tcp --dport %s -j DNAT --to %s:%s' \
                    %(cmd_iptables, '-D', hostport, vmip, vmport)
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

    # if connect:
    #     log.info('Start.')
    #     log.info('Database connected.')
    #     while 1:
    #         query_portreq = "SELECT * FROM %s WHERE state='adding' \
    #                 OR state='deleting 'ORDER BY hostport"%(porttb)
    #         db.query(query_portreq)
    #         req_res = db.store_result()
    #         fetched_req_data = req_res.fetch_row()
    #         while fetched_req_data:
    #             state = fetched_req_data[0][idx_state]
    #             vmname = fetched_req_data[0][idx_vmname]
    #             vmport = fetched_req_data[0][idx_vmport]
    #             oldhostport = fetched_req_data[0][idx_hostport]

    #             if (state == 'adding') :
    #                 vmip = socket.gethostbyname(vmname)
    #                 newport = oldhostport
    #                 if (newport == '-1') :
    #                     newport = get_port()
    #                 if (newport != -1) :
    #                     portmapping(vmname, vmip, vmport, newport, 'a')
    #                     query = "UPDATE %s SET state='using', \
    #                         hostport='%s', ip='%s' \
    #                         WHERE hostport=%s"%(porttb, newport, vmip, oldhostport)
    #                     db.query(query)
    #                 else :
    #                     log.error('No more port!')
    #             elif (fetched_req_data[0][idx_state] == 'deleting') :
    #                 #delete port
    #                 vmip = fetched_req_data[0][idx_ip]
    #                 portmapping(vmname, vmip, vmport, oldhostport, 'd')
    #                 query = "DELETE FROM %s WHERE hostport=%s"%(porttb, oldhostport)
    #                 db.query(query)
    #             else :
    #                 log.error("I don't know what's wrong!")

    #             fetched_req_data = req_res.fetch_row()
    #         time.sleep(sleep_time)
    def sayHello(self):
        print 'Hello'
    
if __name__ == '__main__':
    host, port, console_off = passArguments()
    mymachine = Coordinator( host, port )
    mymachine.run(console_off)

