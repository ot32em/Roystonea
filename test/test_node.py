from Roystonea.scripts.node import Node
from Roystonea.scripts.include import message
from Roystonea.scripts.include import client
from support import message_factory
from mock import MagicMock, ANY
import threading
import random
from time import sleep


HOST = "127.0.0.1"
PORT = random.randrange(20000, 30000)

def test_node():
    message = message_factory.create("NodeCreateVMReq")

    # server
    server = Node(HOST, PORT)
    server.createVMReqHandler = MagicMock(return_value="hello world")

    # test start threading
    server.sayHello = MagicMock(return_value="hello")
    server.start_thread(target=server.sayHello)

    def server_thread():
        server.run()

    t = threading.Thread(target = server_thread)
    t.start()

    # client
    try:
        sleep(3)

        ret = client.send_message((HOST, PORT), message)
        assert ret == "hello world"

        client.sendonly_message((HOST, PORT), message)

    finally:
        server.shutdown()

    server.sayHello.assert_called_with()
    server.createVMReqHandler.assert_called_with(message, ('127.0.0.1', ANY))
