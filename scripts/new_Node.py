from VM_initializer_ubuntu import VM_initializer_ubuntu
import pexpect
from scripts.include import CommonHandler, Client, Message

class Node(CommonHandler):
    def __init__(self, host, port):
        CommonHandler.__init__(self, host, port)

        self.dispatch_handlers.update({
            'ShutdownReq': self.shutdown,
            'NodeHypervisorReq': self.HypervisorReqHandler,
            })
    
    def shutdown(self, req):
        # execute xm shutdown req.vm_id
        shutdown = "xm shutdown "+ str(req.vm_id)
        pexpect.run(shutdown)
        msg = Message.ShutdownRes(msg = "Success", hostname = req.node, vm_id = req.vm_id)
        Client.sendonly_message(self.server.pm_relation.parent_addr)

    def HypervisorReqHandler(self, request):
        print request
        
        if request.type == 'ubuntu':
            VM_initializer = VM_initializer_ubuntu(request.id, request.owner, request.group_num, request.vm_num, request.mem, request.disk, request.cores, request.hostmachine)
            VM_initializer.start()
        
        res = Message.NodeHypervisorRt(status = 'Success', msg = str(request.id) + '-' + request.owner, vm_id = request.id)
        print res.status
        print res.msg
        print request.id

        Client.sendonly_message(self.server.pm_relation.parent_addr,res)

if __name__ == "__main__":
    import sys
    node_machine = Node(sys.argv[1], sys.argv[2])
    node_machine.run()
