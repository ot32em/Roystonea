'''
This is SubsystemManager.py
Remember to type "HOST" and "PORT" arguments when execute SubsystemManager.py
ex. "python Base.py 192.168.15.1 10000"

Note:
(1) You have to convert "HOST" to "int" type
(2) Must crate config file "subsystem_manager_cfg", you can reference other config files

by Teddy, 2012/02/17
'''

from scripts.include.CommonHandler import  passArguments

from scripts.include import CommonHandler

class SubsystemManager(CommonHandler):
    ''' custom init variable '''
    num_rthreads = 4
    FILENAME_MY_CONFIG = 'subsystem_manager_cfg'
    level = 'subsystem_manager'
    
    def __init__(self, host, port):
        CommonHandler.__init__(self, host, port)
        self.dispatch_handlers.update({
            'NetworkingSubsystemPortMappingReq': self.NetworkingSubsystemPortMapping,
            'MonitoringSubsystemPMreq': self.MonitoringSubsystemPM,
        })
        self.startup_functions.extend((
            self.MonitoringSubsystemVM,
            self.StorageSubsystem, # reclaiming space from files that are no longer used
            self.sayHello, # hello function              
        ))
   
    def NetworkingSubsystemPortMapping(self, req):
        pass
    
    def MonitoringSubsystemPM(self, req):
        pass

    def MonitoringSubsystemVM(self):
        pass
    
    def StorageSubsystem(self):
        pass

    def sayHello(self):
        print 'Hello'
    
if __name__ == '__main__':
    host, port, console_off = passArguments()
    mymachine = SubsystemManager( host, port )
    mymachine.run(console_off)

