DEBUG = True

""" db config """
if DEBUG:
    db_host = "140.112.28.240"
else:
    db_host = 'localhost'
db_account = 'root'
db_password = '87888'
db_name = 'roystonea_roystonea'
""" other config  """
level = "coordinator"
num_rthreads = 4
FILENAME_MY_CONFIG = 'Coordinator_cfg'

cmd_iptables = 'sudo iptables -t nat'
