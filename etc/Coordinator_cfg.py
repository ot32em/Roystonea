DEBUG = True

""" global config """
if DEBUG:
    host = "140.112.28.240"
else:
    host = 'localhost'

subsystem_port = 6969

""" db config """
db_account = 'root'
db_password = '87888'
db_name = 'roystonea_2012'

""" other config  """
level = "coordinator"
num_rthreads = 4
FILENAME_MY_CONFIG = 'Coordinator_cfg'

cmd_iptables = 'sudo iptables -t nat'

""" portmapping config """
portmapping_interval = 10
portmpping = "portmapping"
portstatus = "portstatus"
hostport = "hostport"

