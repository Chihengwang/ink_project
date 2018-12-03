import socket
import sys
PORT=8888
def init_socket(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('172.22.11.2', port)
    # print(sys.stderr, 'connecting to %s port %s' % server_address)
    sock.connect(server_address)
    return sock
def send_status(status):
    sock=init_socket(PORT)
    print(status)
    if(status=='empty' or status=='a_few'):
        sock.sendall(str.encode('yes'))
    else:
        sock.sendall(str.encode('no'))
    data = sock.recv(1024)
    print('Received', repr(data))
    if(bytes.decode(data)=='LackOfWater'):
        # print(sys.stderr, 'closing socket')
        sock.close()
        return "WARNING"
    elif(bytes.decode(data)=='no problem'):
        # print(sys.stderr, 'closing socket')
        sock.close()
        return "OKAY"
    else:
        print(sys.stderr, 'closing socket')
        sock.close()
        return "NULL"

if __name__ == '__main__':

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the port where the server is listening
    server_address = ('localhost', 8888)
    print(sys.stderr, 'connecting to %s port %s' % server_address)
    sock.connect(server_address)
    c=0
    try:
        # Send data
        while True:
            if(c==0):
                sock.sendall(str.encode(''))
            if(c==1):
                sock.sendall(str.encode('no'))
            if(c>=2):
                sock.sendall(str.encode('yes'))
            # wait for server's reply.
            data = sock.recv(1024)
            print('Received', repr(data))
            if(bytes.decode(data)=='Sucessfully'):
                break
            else:
                c+=1
                continue
    finally:
        print(sys.stderr, 'closing socket')
        sock.close()