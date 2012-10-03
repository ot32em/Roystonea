'''
This is Algorithm.py
Remember to type "HOST" and "PORT" arguments when execute Algorithm.py
ex. "python Algorithm.py 192.168.10.1 10000"

## You have to convert "HOST" to "int" type

by Radstar Yeh, Teddy, 2012/02/14
'''

from scripts.include.CommonHandler import  passArguments
from scripts.include import CommonHandler

class Algorithm(CommonHandler):
    ''' custom init variable '''
    num_rthreads = 4
    FILENAME_MY_CONFIG = 'Algorithm_cfg'
    level = 'algorithm'
    
    def __init__(self, host, port):
        CommonHandler.__init__(self, host, port)
        self.dispatch_handlers.update({
            'RackAlgorithmReq': self.RackAlgorithm,
        })
        self.startup_functions.extend((
            self.sayHello, # hello function
        ))
   
    def RackAlgorithm(self, req):
        vm_id = req.vm_id
        vm_cpu = req.cpu
        vm_mem = req.mem
        vm_disk = req.disk
        pm_resource_list = req.pm_resource_list
        
        # first-fit to scheduule VM on PM
        for pm in pm_resource_list:
            if vm_cpu <= pm['cpu'] and vm_mem <= pm['mem'] and vm_disk <= pm['disk']:
                print( 'put vm' + str(vm_id) + ' on ' + pm['hostname'])
                return pm['hostname']

        return 'No host machine for VM'

    def sayHello(self):
        print ('Hello')
    
if __name__ == '__main__':
    host, port, console_off = passArguments()
    mymachine = Algorithm( host, port )
    mymachine.run(console_off)

