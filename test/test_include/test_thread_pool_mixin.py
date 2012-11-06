import SocketServer
import threading
import socket
from Roystonea.scripts.include.thread_pool_mix_in import ThreadPoolMixIn

class MyTCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        self.data = ""
        while True:
            data = self.request.recv(1024)
            if not data: break
            self.data += data

        self.request.sendall(self.data)

class ThreadedTCPServer(ThreadPoolMixIn, SocketServer.TCPServer):
    pass

HOST, PORT = "localhost", 9999
server = ThreadedTCPServer((HOST, PORT), MyTCPHandler)

def server_thread():
    server.serve_forever()

def test():
    data = "hello world"

    # start server
    t = threading.Thread(target = server_thread)
    t.start()

    # client
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        sock.sendall(data)
        sock.shutdown(socket.SHUT_WR)
        assert sock.recv(1024) == data
    finally:
        sock.close()
        server.shutdown()
