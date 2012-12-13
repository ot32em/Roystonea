from include.base_server import BaseServer
from include import message
from include import config
from database import VM
from database import Database

class Coordinator(BaseServer):

    def __init__(self, host, port):
        super(Coordinator, self).__init__(host, port)
        self.algorithm_addr = None 

    def register_handle_functions(self):
        self.register_handle_function("ClusterCreateVMRes", self.createVMResHandler)
        self.register_handle_function("CoordinatorUpdateMonitorResultReq", self.updateMonitorResultHandler )


    def updateMonitorResultHandler(self, msg, client_addr=None):
        print("coordinator@upateMonitiorResultHandler called!")
        db = Database.singleton()

        vm_status_list = msg.vm_status_list
        machine_resource_list = msg.machine_resource_list

        for vm in vm_status_list:
            sql = "update `vm` set `usage_cpu`='%f', `usage_memory`='%i', `hostmachine`='%s' where `vmid`='%s'" %  \
                ( vm['cpu_usage'], vm['used_memory'], vm['hostmachine'], vm['vmid'] )
            print( sql )
            db.query( sql )
        for machine_resource in machine_resource_list :
            sql = "update `resource` set `disk_remaining`='%i' where `hostname`='%s'" %  \
                ( machine_resource['remaining_disk'], machine_resource['addr'] )
            print(sql)
            db.query( sql )


    def register_start_functions(self):
        return
        VM.register_event_callback("start_vm_record_inserted", self.create_vm)
        self.register_start_function(VM.start_pooling)

    def createVMResHandler(self, msg, client_address=None):
        ''' Get new VM host node ip, and let moniter to check the VM status 

        Currently, just write to db that the vm is ready
        '''
        vm_request = self.pop_context(msg)
        if not vm_request: return

        vm_request.update_vmstatus("running")
        print "update!"

    def create_vm(self, vm_request):
        # this is for test, should be fetch from database
        values = vm_request.to_create_vm_request_values()


        # ask algorithm
        addr = self.algorithm_addr
        select_cluster_msg = self.create_message(message.AlgorithmSelectClusterListReq, values)
        addr_result = self.send_message(addr, select_cluster_msg)

        cluster_addr = addr_result[0]

        create_vm_msg = self.create_message(message.ClusterCreateVMReq, values)
        self.send_message(cluster_addr, create_vm_msg, context=vm_request)

def start(port, algo_addr):
    import threading
    from time import sleep

    server = Coordinator("127.0.0.1", port)
    server.algorithm_addr = algo_addr

    def start_server():
        server.run()

    t = threading.Thread(target = start_server)
    t.start()

    sleep(5)
    server.create_vm(None)

def load_setting():
    server = Coordinator("127.0.0.1", 5001)
    print server.database_config
