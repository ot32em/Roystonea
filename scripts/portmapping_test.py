import socket

def portmapping(vmname, vmip, vmport, hostport, action):
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

# action should be 'a' or 'd'
def test(action):
    print 'test from portmapping_test.py'
    vm_name = 'royuser-1-1'
    vm_ip = socket.gethostbyname(vm_name)
    portmapping(vm_name, vm_ip, 22, 2022, action)

