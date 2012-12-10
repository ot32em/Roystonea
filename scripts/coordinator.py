from include.base_server import BaseServer
from include import message
from include import config
from database import VM

class Coordinator(BaseServer):

    def __init__(self, host, port):
        super(Coordinator, self).__init__(host, port)
        self.algorithm_addr = None 

    def register_handle_functions(self):
        self.register_handle_function("ClusterCreateVMRes", self.createVMResHandler)
        self.register_handle_function("CoordinatorUpdateMonitorResultReq", self.updateMonitorResultHandler )


    def updateMonitorResultHandler(self, msg, client_addr=None):
        print("coordinator@upateMonitiorResultHandler called!")

        vm_status_list = msg.vm_status_list
        machine_resource_list = msg.machine_resource_list

        print("vm_status_list: "),
        for vm in vm_status_list:
            print( "[%s@%s]," % (vm['vmid'], vm['used_memory'])),
        print("machine_resource_list: "),
        print(machine_resource_list)

<<<<<<< HEAD
=======

    def register_start_functions(self):
        VM.register_event_callback("start_vm_record_inserted", self.create_vm)
        self.register_start_function(VM.start_pooling)
>>>>>>> 19ec7390d48240103afe4473a8cca46e534fdd70

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
        select_cluster_msg = self.create_message(message.AlgorithmSelectClusterReq, values)
        cluster_addr = self.send_message(addr, select_cluster_msg)

        create_vm_msg = self.create_message(message.ClusterCreateVMReq, values)
<<<<<<< HEAD
        self.send_message(cluster_addr, create_vm_msg, context=None)

class Database(object):
    _database = None
    def __init__(self):
        self.config = config.load("database")
        self.db = None

    @classmethod
    def singleton(self):
        if self._database == None:
            self._database = Database()
            self._database.connect()
        return self._database

    def connect(self):
        print self.config
        self.db = MySQLdb.connect(self.config['host'], 
                self.config['username'], 
                self.config['password'], 
                self.config['database'])

    def query(self, query_string):
        self.db.query(query_string)

    def store_result(self):
        return self.db.store_result()

class VM(namedtuple("VM", [ "vmid", 
                            "vmlabel",
                            "groupid",
                            "vmsubid",
                            "vmname",
                            "ownerid",
                            "vmtype",
                            "vmstatus",
                            "time_created",
                            "time_lastupdated",
                            "time_minutes_stall",
                            "config_cpu",
                            "config_memory",
                            "config_disk",
                            "config_lifttime",
                            "usage_cpu",
                            "usage_memory",
                            "usage_disk",
                            "hostmachine",
                            "price_hout"
                            ])):
    #database = Database.singleton()

    @classmethod
    def find_all_by_vmstatus(self, status):
        query = "SELECT * FROM vm WHERE vmstatus = '%s'" % status
        print query
        self.database.query(query)
        result = self.database.store_result()

        objects = []
        while True:
            row = result.fetch_row()
            if len(row) > 0:
                objects.append(VM(*row[0]))
            else:
                break

        return objects
=======
        self.send_message(cluster_addr, create_vm_msg, context=vm_request)
>>>>>>> 19ec7390d48240103afe4473a8cca46e534fdd70

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
