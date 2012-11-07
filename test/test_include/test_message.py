from Roystonea.scripts.include import message

def test_create_message_class():
    req = message.NodeCreateVMReq('vmid', 'groupid', 'vmsubid', 'ownerid', 'vmtype', 
            'config_cpu', "config_memory", 'config_disk', 'time_life', ('127.0.0.1', 5678), 0)

    assert req.vmid == 'vmid'
