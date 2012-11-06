from Roystonea.scripts.include import message
from Roystonea.scripts.include.base_server import BaseServer
from Roystonea.scripts.include import client
import pickle
import threading

HOST, PORT = "localhost", 5000

# handle functions for test
def hello(data):
    return "hello " + data.name

def helloworld():
    return "hello"

def test_register_handle_funtion():
    server = BaseServer(HOST, PORT)
    server.register_handle_function("helloworld", helloworld)
    assert server.handle_functions["helloworld"]() == "hello"

def test_unregister_handle_function():
    server = BaseServer(HOST, PORT)
    server.register_handle_function("helloworld", helloworld)
    assert server.handle_functions["helloworld"]() == "hello"

    server.unregister_handle_function("helloworld")
    assert server.handle_functions.has_key("helloworld") == False


# setting for test unpack_and_execute
class CmdHello:
    def __init__(self, name):
        self.name = name

message.CmdHello = CmdHello

def test_unpack_and_execute():
    cmd = CmdHello("world")
    data = pickle.dumps(cmd)

    server = BaseServer(HOST, PORT)
    server.register_handle_function("CmdHello", hello)
    message_name, ret = server.unpack_and_execute(data)

    assert message_name == "CmdHello"
    assert ret == "hello world"

def test_base_server():

    # server
    server = BaseServer(HOST, PORT)
    server.register_handle_function("CmdHello", hello)
    def server_thread():
        server.run()

    t = threading.Thread(target = server_thread)
    t.start()

    # client
    try:
        ret = client.send_message((HOST, PORT), CmdHello("world"))
        assert ret == "hello world"

    finally:
        server.shutdown()
