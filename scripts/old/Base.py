'''
This is Base.py
Remember to type "HOST" and "PORT" arguments when execute Coordinator.py
ex. "python Base.py 192.168.10.1 10000"

Note:
(1) You have to convert "HOST" to "int" type
(2) Must crate config file "Base_cfg", you can reference other config files

by Teddy, 2012/02/09
'''

from scripts.include.CommonHandler import  passArguments
from scripts.include import CommonHandler

class Base(CommonHandler):
    ''' custom init variable '''
    num_rthreads = 4
    FILENAME_MY_CONFIG = 'Base_cfg'
    level = "base"
    
    def __init__(self, host, port):
        CommonHandler.__init__(self, host, port)
        # function name should change!!!
        self.dispatch_handlers.update({
            'Message.py function name': self.functionName,
        })
        self.startup_functions.extend((
            self.sayHello,               # hello function
        ))
   
    # when receive msg from other server, do the following thing 
    def functionName(self, req):
        pass   

    def sayHello(self):
        print 'Hello'
    
if __name__ == '__main__':
    host, port, console_off = passArguments()
    mymachine = Coordinator( host, port )
    mymachine.run(console_off)

