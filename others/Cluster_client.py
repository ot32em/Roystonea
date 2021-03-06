import socket
import pickle
from scripts.include import Message

HOST, PORT = "localhost", 7003


# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

req1 = Message.ClusterVirtualMachineManagerReq(id='86888', 
					       name='me', 
					       owner='elalic', 
					       type='gentoo', 
					       mem=4, 
					       disk=20, 
					       cores=4)
req3 = Message.GetAvailablePhysicalMachineReq(auth='hi')
data = pickle.dumps(req3)
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
