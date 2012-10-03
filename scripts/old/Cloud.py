'''
This is Cloud.py
Remember provide arguments HOST and PORT when exec Rack.py, like "python Cloud.py 140.112.1.23 4567 "
,and convert host to int type

by Elalic, 2011.08.13
and by Ot Chen 2011.10.31
'''

from scripts.include.CommonHandler import  passArguments
from time import sleep
from scripts.include import CommonHandler

class Cloud(CommonHandler):
    ''' custom init variable '''
    FILENAME_MY_CONFIG = 'Cloud_cfg'
    num_rthreads = 4
    level = "cloud"

    def __init__(self, host, port):
        CommonHandler.__init__(self, host, port)
        self.dispatch_handlers.update({
            'GetAvailableClustersReq': self.GetAvailableClusters,
        })
        self.startup_functions.extend((
            self.periodlySampleFunction,
            self.normalSampleFunction, # It's a example to show how to add startup functions
        ))

    def periodlySampleFunction(self):
        interval = 30 # secs
        while True:
            #Doing something and periodly issue
            sleep(interval)

    def normalSampleFunction(self):
        #Doing something you want at server startup time
        pass

    def GetAvailableClusters(self, req):
        ret = None
        try:
            import imp
            tmp = imp.load_source('', self.config.get('CloudComponentsPath')).CloudCoordinator()
            ret = tmp.GetAvailableClusters(req, self.cfg)
            #ret = Message.RackHypervisorReqRt(status='Success', msg=req.id + '-' + req.owner)
        except Exception, e:
            #Error msg
            print str(e)
        return ret

if __name__ == '__main__':
    host, port, console_off = passArguments()
    mymachine = Cloud(host, port)
    mymachine.run(console_off)

