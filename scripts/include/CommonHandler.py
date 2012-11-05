# old, to be refactored script
if False:
    import time
    from time import sleep
    import socket
    import copy
    from scripts.include import CommonServer, Client, Message

    '''
          +---------------+
          | CommonHandler |
          +---------------+
            |      +----------+
            |----> | Cloud.py |
            |      +----------+
            |      +------------+
            |----> | Cluster.py |
            |      +------------+
            |      +---------+
            |----> | Rack.py |
            |      +---------+
            |      +---------+
            |----> | Node.py |
                   +---------+


            CommonHandler <---- dispatch_handlers, Human writes api here.
                  |
                run()
                  |
                  V
            CommonServer  <-----  request, server listen request put pool
                  |
         processPoolRequest()
                  |
                  V
         RequestDispatchClass
                  |
              handle() ----------> res = dispatch_handlers[req.__class__.__name__](req)
                                   send_back( res)
                



         +-----------------------------------------------------------------------------------+
         | Important:                                                                        |
         |    Launching each handler script NEED give host and port of server as parameter   |
         |    ex: python Cloud.py 140.112.123.234 7003                                       |
         +-----------------------------------------------------------------------------------+
          
         CommonHandler
            class variables
                > FILENAME_DEFAULT_CONFIG @ string, default config filename.
                > FILENAME_MY_CONFIG @ string, specific local config filename.

                > dispatch_handlers @ dictionary, key is message format name, value is function binding.
                > startup_handlers @ list, entry is function binding.
                > num_rthreads @ int, how many threads handler the request in pool.

            object variables:
                > host @ string, ip or domain name.
                > port @ int, port.
                > addr @ 2-tuple with (host, port).

                > pm_relation @ PM_Entry class, 
                    pm_relation.label @ string, server's codename.
                    pm_relation.addr @ 2-tuple of self's address.
                    pm_relation.parent_addr @ 2-tuple of parent's address.
                    pm_relation.children_addrs @ list of children's addresses.

                > config @ dictionary, 
                    key @ string, config's name, 
                    value @ string, config's value, 
                    inited by performing loadConfig().

            object methods:
                > run 
                    Instanciate server and run it. 
                    Pass 1.dispatch_handlers, 2.startup_functions, and 3.RequestDispatchClass to server.
                > setConfig/loadConfig
                    Load config file to config variable. storing about static information.


    '''

    class CommonHandler():
    # Provide platform to write functions of two type , startup function and 
    # request-based functions.

        FILENAME_CONFIG_DIR = '/mnt/images/nfs/new_roystonea_script/teddy_roystonea_script/'
        FILENAME_DEFAULT_CONFIG = 'default_cfg'
        FILENAME_MY_CONFIG = ''
        level = 'prototype'

        num_rthreads = 4

        # Functions bound in startup_functions will perform at server start.

        def __init__(self, host, port):
            self.host = host
            self.port = int(port)
            self.addr = (host, int(port))

            # Record Label, Addr, Parent Addr, Children Addrs and something about hierachy

            self.loadConfig()  # load some static setting stored in file.

            # Functions bound in dispatch_handlers will be triggered by request to perform.
            self.dispatch_handlers= { 
                'CmdShutdownTheChildrenReq': self.CmdShutdownTheChildren, # Shutdown remote machine 's children.
                'CmdShutdownChildrenReq': self.CmdShutdownChildren, # Shutdown self's children
                'CmdShutdownTheReq': self.CmdShutdownThe,       # Shutdown specific machine
                'CmdShutdownReq': self.CmdShutdown,             # Recv shutdown order.
                'CmdFreezeRThreadReq': self.CmdFreezeRThread,   # Freeze the current thread who catch this request.
                'CmdGetPingReq': self.CmdGetPing,                  # Ping other CommonHandler-based machine, and return msg.
                'CmdPingReq': self.CmdBePinged,                    # Be ping, just return emtpy for testing network status.
                'CmdGetPMRelationReq': self.CmdGetPMRelation,   # Return the current pm_relation.
                'CmdSetPMRelationReq': self.CmdSetPMRelation,   # Set the pm_relation.
                'CmdGetThePMRelationReq': self.CmdGetThePMRelation,
                'CmdSetThePMRelationReq': self.CmdSetThePMRelation,
                'CmdGetChildrenPMRelationsReq': self.CmdGetChildrenPMRelations,
                'CmdUpdatePMRelationReq': self.CmdUpdatePMRelation,
                'CmdGetParentReq': self.CmdGetParent,           # Get the parent address.
                'CmdSetParentReq': self.CmdSetParent,           # Set the parent address.
                'CmdGetChildrenReq': self.CmdGetChildren,       # Get the children addresses as list.
                'CmdSetChildrenReq': self.CmdSetChildren,       # Set the children addresses.
                'CmdAddChildReq' : self.CmdAddChild,
            }
            self.startup_functions= [ self.showPMRelation , ]

        def run(self, console_off=False ):
        # Instantiate the server instance , and start it.
            self.server = CommonServer(self.addr, 
                                       self.level,
                                       self.num_rthreads, 
                                       self.dispatch_handlers, 
                                       self.startup_functions)
            self.server.serve_forever(console_off)

        ''' Class methods '''

        def loadConfig(self):  
        # Load default config first, then load my-config to overwrite data with the name

            # Let cfg_dict be the global_variable space in execfile method performing.
            cfg_dict = dict()
            cfg_filename = self.FILENAME_CONFIG_DIR + self.FILENAME_DEFAULT_CONFIG
            execfile(cfg_filename, cfg_dict)
            
            # Let local setting overwrite default setting
            if self.FILENAME_MY_CONFIG :
                my_cfg_dict = dict()
                my_cfg_filename = self.FILENAME_CONFIG_DIR + self.FILENAME_MY_CONFIG 
                execfile(my_cfg_filename, my_cfg_dict)
                ''' Let local override global '''
                for k in my_cfg_dict.keys():
                    cfg_dict[k] = my_cfg_dict[k]
            # clean up bulltin module in globals, it useless.
            del cfg_dict['__builtins__']
            
            self.config = cfg_dict

        def setConfig(self, cfg_dict, overwrite=False): 
        # set config
            if overwrite :
                self.config = cfg_dict
            else:
                self.config.update(cfg_dict)


        ''' Main methods ''' 
        def setThePMRelation(self, addr, pm_relation):
            req = Message.CmdSetPMRelationReq( pm_relation = pm_relation )
            res = Client.send_message( addr, pm_relation )
            return res
        
        def getChildrenPMRelations(self):
            pm_relations = list()
            for addr in self.server.pm_relation.children_addrs :
                req = Message.CmdGetPMRelationReq()
                res = Client.send_message( addr, req )
                pm_relations.append(res )
            return pm_relations


        def getPMRelation(self):
        # I hope every function defined by user should use getPMRelation method to get
        # a of PMRelation by call-by-value  to know its hierrachy. Because it may cause     
        # inconsistent when pm_relation was modified during processing the request or
        # other works if you ref the self.server.pm_relation.
            return copy.deepcopy(self.server.pm_relation)

        def setPMRelation(self, relation):
            self.server.pm_relation.overwrite(relation)

        def updatePMRelation(self, relation ):
            self.server.pm_relation.update( relation)

        def showPMRelation(self):
            print( self.server.pm_relation.dump_pretty() )

        ''' Requests-based Methods '''

        def CmdShutdownChildren(self, req):
            req_shutdown = Message.CmdShutdownReq(chain_shutdown = req.chain_shutdown)
            for addr in self.server.pm_relation.children_addrs :
                res = Client.send_message( addr, req_shutdown )
            return Message.CmdShutdownTheRes()

        def CmdShutdownTheChildren(self, req):
            dest_addr = req.dest_addr
            req = Message.CmdShutdownChildrenReq(chain_shutdown = req.chain_shutdown)
            res = Client.send_message( dest_addr, req )
            return Message.CmdShutdownTheChildrenRes()


        def CmdShutdownThe(self, req):
            addr = req.dest_addr
            req = Message.CmdShutdownReq(chain_shutdown = req.chain_shutdown)
            res = Client.send_message( addr, req )
            return Message.CmdShutdownTheRes()

        def CmdShutdown(self, req):
            sleep(req.after_secs)
            if req.chain_shutdown :
                req_shutdown = Message.CmdShutdownReq()
                for addr in self.server.pm_relation.children_addrs :
                    try:
                        res = Client.send_message( addr, req_shutdown )
                        print( "child@{addr} closed.".format( addr= '%s:%d'% ( addr[0],addr[1]) ) )
                    except Exception as e:
                        print( "child@{addr} failed to close. error msg: {msg}".format( addr= '%s:%d'% ( addr[0],addr[1]), msg='%s'%e ) )

            
            self.server.threadCallShutdown()
            print( 'Ready to close self')
            return Message.CmdShutdownRes()

        def CmdFreezeRThread(self, req):
            sleep(req.secs)
            return Message.CmdFreezeRThreadRes()

        def CmdGetPing(self, req):
            from_addr = self.addr
            dest_addr = req.dest_addr
            times = req.times
            msg = ''

            req = Message.CmdPingReq()
            try:
                for i in xrange(times):
                    start = time.time()
                    res = Client.send_message( dest_addr, req )
                    intval = time.time() - start
                    msg += '{times} trial: from {fromaddr} pings {destaddr} in {secs}\n'.format(times=times, fromaddr=from_addr, destaddr=dest_addr, secs = intval )
            except socket.error:
                msg += 'Fail to connect to {destaddr}'.format( destaddr = dest_addr )
            return Message.CmdGetPingRes( msg = msg )

        def CmdBePinged(self, req):
            return Message.CmdPingRes()

        def CmdGetPMRelation(self, req):
            r = self.getPMRelation()
            return Message.CmdGetPMRelationRes(
                pm_relation = r, 
                dump_one_row = '%s' % r, 
                dump_two_rows = r.dump_two_rows(), 
                dump_children_rows = r.dump_children_rows(), 
                dump_pretty = r.dump_pretty() )

        def CmdSetPMRelation(self, req ):
            self.setPMRelation(req.pm_relation)
            return Message.CmdSetPMRelationRes()

        def CmdGetThePMRelation(self, req): # get specific machine's pm_relation @ addr
            addr = req.dest_addr
            req = Message.CmdGetPMRelationReq()
            res = Client.send_message( addr, req )
            return Message.CmdGetThePMRelationRes( pm_relation = res.pm_relation,
                    dump_one_row = res.dump_one_row,
                    dump_two_rows = res.dump_two_rows,
                    dump_children_rows = res.dump_children_rows,
                    dump_pretty = res.dump_pretty )
        
        def CmdSetThePMRelation(self, req):
            addr = req.dest_addr
            pm_relation = req.pm_relation
            res = self.setThePMRelation( addr, pm_relation )
            return Message.CmdSetThePMRelationRes()

        def CmdGetChildrenPMRelations(self, req):
            res_pm_relations = self.cmdGetChildrenPMRelations()
            return Message.CmdGetChildrenPMRelationsRes( res_pm_relations = res_pm_relations )

        def CmdUpdatePMRelation(self, req):
            self.updatePMRelation(req.pm_relation)
            return Message.CmdUpdatePMRelationRes()

        def CmdGetParent(self, req):
            parent = self.server.pm_relation.parent_addr
            return Message.CmdGetParentRes(parent_addr=parent)
        def CmdSetParent(self, req):
            parent = req.parent_addr
            self.server.pm_relation.setParentAddr(parent)
            return Message.CmdSetParentRes()

        def CmdGetChildren(self, req):
            children = self.server.pm_relation.children_addrs
            return Message.CmdGetChildrenRes( children_addrs = children )
        def CmdSetChildren(self, req):
            children = req.children_addrs
            self.server.pm_relation.setChildrenAddrs( children)
            return Message.CmdSetChildrenRes()

        def CmdAddChild(self, req):
            child_addr = req.child_addr
            if not child_addr in self.server.pm_relation.children_addrs :
                self.server.pm_relation.children_addrs.append( child_addr ) 
            return Message.CmdAddChildRes()


    def passArguments():
        import sys 
        errmsg = 'usege(pick Cluster.py for example): \n \tpython Cluster.py machine\'s HOST machine\'s PORT [console_off]'
        isFalse = False
        if len( sys.argv )  <= 2 :
            print( 'Too few arguments' )
            isFalse = True

        host = sys.argv[1]
        if sys.argv[1]: # check host
            pass

        port = sys.argv[2]  # check port
        if not port.isdigit() :
            print( 'port must be int and range: 1~65535' )
            isFalse = True
        elif int(port) < 0 or int(port) > 65535 :
            print( 'port must be int and range: 1~65535' )
            isFalse = True

        console_off = False
        if len( sys.argv ) >= 4 : # has console_off
            if sys.argv[3].lower().strip() == 'console_off' :
                console_off = True

        if isFalse :
            print( errmsg )
            raise SystemExit

        return ( host, port, console_off )
