import socket
import pickle

def send_message( address, message, timeout=10.0 ) : # it will send message, then recv the response message
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout( timeout )
    sock.connect(address)

    # send object 
    message_serial = pickle.dumps( message )
    sock.send(message_serial)
    sock.shutdown(socket.SHUT_WR)

    # Receive data from the server and shut down
    received = ''
    input = True
    while input:
        input = sock.recv(4096)
        received += input
    recv_message = pickle.loads(received)
    sock.close()

    return recv_message

def sendonly_message( address, message) : # it will only send message, then shutdown socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    retry = True
    counter = 0
    while counter < 10 and retry:
        sleep(1)
        try:
            retry = False
            sock.connect( address )
            message_serial = pickle.dumps( message )
            sock.send(message_serial)
        except:
            counter += 1
            retry = True

    sock.close()
