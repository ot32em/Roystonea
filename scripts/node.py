from include.base_server import BaseServer
from include import client
from include import message
from vm_manager.vm_ubuntu_manager import VMUbuntuManager
import pydaemon, signal

class Node(BaseServer):

    level = "node"

    def __init__(self, host, port):
        super(Node, self).__init__(host, port)

    def register_handle_functions(self):
        self.register_handle_function("NodeCreateVMReq", self.createVMReqHandler)

    def createVMReqHandler(self, msg, client_address=None):
        self.createVM(msg)

        status = "ok"
        res_msg = self.create_message(message.NodeCreateVMRes, [msg.vmid, status], context=msg)
        self.send_message(msg.caller_address, res_msg)

    def createVM(self, msg):
        if msg.vmtype == "ubuntu":
            owner = str(msg.ownerid) # TODO
            hostmachine = "ignore now" # TODO
            vm_manager = VMUbuntuManager(msg.vmid, 
                    owner, 
                    msg.groupid, 
                    msg.vmsubid, 
                    msg.config_memory, 
                    msg.config_disk, 
                    msg.config_cpu, 
                    hostmachine)
        vm_manager.start()

pidfile = "/tmp/roystonea.node.pid"
default_port = 8001

class NodeDaemon(pydaemon.Daemon):
    port = default_port

    def run(self):
        server = Node("127.0.0.1", self.port)

        def register_sigterm_handler():
            def sigterm_handler(signal, frame):
                server.shutdown()

            signal.signal(signal.SIGTERM, sigterm_handler)

        server.register_start_function(register_sigterm_handler)
        server.run()

def getDaemon():
    return NodeDaemon(pidfile = pidfile)

def start(options):
    print "start node server"
    port = default_port
    if not options.has_key('daemonize'): options['daemonize'] = True 
    if options['daemonize']:
        daemon = getDaemon()
        daemon.start()
    else:
        server = Node("127.0.0.1", port)
        server.run()

def stop(options):
    daemon = getDaemon()
    daemon.stop()
