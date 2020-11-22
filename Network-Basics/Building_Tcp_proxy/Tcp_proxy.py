# credits --> black hat python justin seitz
'''proxy is a server that acts as an intermediary between a client and the destination server. Clients establish connections to the TCP proxy server, 
which then establishes a connection to the destination server'''
# importing packages
import socket
import sys
import threading
from numba import unicode
from pygments.util import xrange
from scapy.all import wrpcap  

def server_side(local_host, local_port, remote_port, remote_host, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        #print(type(local_host), type(local_port))
        server.bind((local_host, local_port))
    except Exception as a:
        print(a)
        print('failed to listen on {}:{}'.format(local_host, local_port))
        print('Check for other listening sockets')
        sys.exit(0)
    print('listening on {}:{}'.format(local_host, local_port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        print('Received incoming connection from {}:{}'.format(addr[0],addr[1]))

        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()
def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    try:
        'handles the sending and the receiving to either side of the data stream'
        # connecting to the remote host
        print('connecting to {} at port {}'.format(remote_host, remote_port))
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect((remote_host, remote_port))
        print('connected to remote host')
    except Exception:
        print('Connection to remote host unsuccessful')


    # receive data from the remote end if necessary
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        #print(remote_buffer)
        #hexdump(remote_buffer)

        # send it to our response handler
        remote_buffer = response_handler(remote_buffer)
        print(remote_buffer)
        # if we have data to send our local client,send it

        if len(remote_buffer):
            print('Sending %d bytes to localhost'%len(remote_buffer))
            client_socket.send(remote_buffer.encode())
    
    # now lets loop and read from local, send to remote and send to local
    while True:
        # read from localhost
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            print('Received %d bytes from localhost'%len(local_buffer))
            #hexdump(local_buffer)

            # send it to our request handler
            local_buffer = request_handler(local_buffer)

            # send off the data to our remote host
            remote_socket.send(local_buffer)
            print('===> Sent to remote')
        
        # receive back the response
        remote_buffer = receive_from(remote_socket)

        if len(remote_buffer):
            print("Received %d bytes from remote."%len(remote_buffer))
            #hexdump(remote_buffer)

            # send the response back to the local socket
            client_socket.send(remote_buffer)
            print('==> Sent to localhost')

        # if no data on the either side, closes connection
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print('No more data...Closing connection')

            break

def hexdump(src, length=16):
    'hex dumping function'
    result = []
    digits = 4 if isinstance(src, str) else 2
    for i in xrange(0,len(src), length):
        a = src[i:i+length]
        hexa = b''.join(['%0*X'%(digits, ord(str(x))) for x in a])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in a])
        result.append(b"%04X %-*s %s" % (i, length*(digits+1),hexa, text))

    print(b'\n'.join(result))

def receive_from(connection):
    buffer = ''.encode()
    # we set a 2 second timeout 
    connection.settimeout(2)

    try:
        # keep reading into the buffer until there's no more data or timeout
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception as e:
        print(e)
    return buffer
def request_handler(buffer):
    'function to modify the requests sent to the remote host'
    #wrpcap('sent_to_host.pcap',buffer)
    # perform packets modifications
    return buffer

def response_handler(buffer):
    'modify any responses destined for the local host'
    # perform packet modifications
    return buffer


def main():
    if len(sys.argv[1:]) != 5:
        print('Usage python Tcp_proxy.py [localhost] [localport] [remotehost] [remoteport] [receive first]') 
        sys.exit(0)
    
    # setting up local listening parameters
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    remote_port = int(sys.argv[4])
    remote_host = sys.argv[3]

    # this tells our proxy to either connect and receive data before sending the data to the remote host
    receive_first = sys.argv[5]

    if 'True' in receive_first:
        receive_first = True
    else:
        receive_first = False

    #print(local_host, local_port, remote_host, remote_port)
    # starting out listening socket
    server_side(local_host, local_port, remote_port, remote_host, receive_first)

main() 

    
