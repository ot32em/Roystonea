import MySQLdb
from collections import namedtuple
from include import config
from time import sleep

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
        self.db = MySQLdb.connect(self.config['host'], 
                self.config['username'], 
                self.config['password'], 
                self.config['database'])
        self.db.autocommit(True)

    def query(self, query_string):
        self.db.query(query_string)

    def store_result(self):
        return self.db.store_result()

class BaseMixin(object):
    event_handlers_dict = {}

    @classmethod
    def register_event_callback(cls, event_name, handler):
        if event_name not in cls.event_handlers_dict:
            cls.event_handlers_dict[event_name] = []

        event_handlers = cls.event_handlers_dict[event_name]
        if handler not in event_handlers:
            event_handlers.append(handler) 

    @classmethod
    def unregister_event_callback(cls, event_name, handler):
        if cls.event_handlers_dict[event_name] == None:
            return 

        event_handlers = cls.event_handlers_dict[event_name]
        if handler in event_handlers:
            event_handlers.remove(handler) 

    @classmethod
    def trigger_event(cls, event_name, obj):
        event_handlers = cls.event_handlers_dict[event_name]
        if event_handlers == None: return

        for handler in event_handlers:
            handler(obj)



class VM(BaseMixin, namedtuple("VM", [ "vmid", 
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

    database = Database.singleton()

    @classmethod
    def find_all_by_vmstatus(self, status):
        query = "SELECT * FROM vm WHERE vmstatus = '%s'" % status
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

    @classmethod
    def pooling_vmstatus_prepare_to_start(cls):
        records = cls.find_all_by_vmstatus("prepare_to_start")
        for record in records:
            cls.trigger_event("start_vm_record_inserted", record)

    @classmethod
    def start_pooling(cls):
        while True:
            cls.pooling_vmstatus_prepare_to_start()
            sleep(10)

    def to_list(self):
        values = []
        for f in self._fields:
            values.append(self[f])

        return values

    def update_vmstatus(self, vmstatus):
        # self.vmstatus = vmstatus
        query = "UPDATE vm SET vmstatus='%s' WHERE vmid=%s" % (vmstatus, self.vmid)
        self.database.query(query)

def db():
    print VM.find_all_by_vmstatus("prepare_to_start")

