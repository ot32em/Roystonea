import socket
import pickle
from scripts.include import Message

HOST, PORT = "localhost", 7001


# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

req1 = Message.NodeHypervisorReq(id='86888', name='me', owner='elalic', type='gentoo', mem=4, disk=20, cores=4)
req2 = Message.NodeStorageReq()
data = pickle.dumps(req1)
sock.send(data)
sock.shutdown(socket.SHUT_WR)

# Receive data from the server and shut down
received = ''
input = True
while input:
	input = sock.recv(1024)
	received += input
ret = pickle.loads(received)
sock.close()

print ret.msg
#print 'status=' + ret.status
#print 'msg=' + ret.msg
