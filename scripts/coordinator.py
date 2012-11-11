from include.base_server import BaseServer
from include import message

class Coordinator(BaseServer):

    def __init__(self, host, port):
        super(Coordinator, self).__init__(host, port)

    def register_handle_functions(self):
        self.register_handle_function("RackCreateVMRes", self.createVMResHandler)

    def createVMResHandler():
        ''' Get new VM host node ip, and let moniter to check the VM status 

        Currently, just write to db that the vm is ready
        '''
        pass

