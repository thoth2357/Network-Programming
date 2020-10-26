# importing packages
import socket
import threading 
import sys
import subprocess
import getopt



def usage():
    print('Net tool\n')
    print('Usage;python_netcat2.py -t target_host -p port')
    print('Options')
    print('-l --listen\t\t-listen on [host]:[port] for incoming connections')
    print('-e --execute-\t\t-execute the given file upon receiving a connection')
    print('-u --upload-destination\t\t -upon receiving connection upload a file and write to [destination]\n\n\n')

    print('Examples for creating a server to upload a file, execute a command, start a command shell')
    print('python_netcat.py -c -p 5454 -l 127.0.0.1') # creates server for command for command shell
    print('python_netcat.py" -e \'ls -l\' -p 9998  -l 127.0.0.1') # creates a server to execute the ls -l command
    

    print('python_netcat.py -t 127.0.0.1 -p 5454')
    print('python_netcat.py -t 127.0.0.1 -p 5454 -l -u=c:\\target.exe')
    print('python_netcat.py -t 127.0.0.1 -p 5454 -e=\"cat /etc/passwd\"')
    print('echo "Welcome" | ./python_netcat.py -t 127.0.0.1 -p 80')
    sys.exit(0)

def handle_client(client_socket,addr,destination, execute, command):
    'function that handles the client for the server'
    print('Server received packets from {}'.format(addr))

    # checking for upload
    if len(destination):
        print('Uploading Sequence active.')
        # read all bytes and write to our destination
        file_buffer = ''.encode()
        
        # keep reading data until none is available
        while True:
            received = client_socket.recv(4096)
            
            if not received:
                break
            else:
                file_buffer += received
        
        # taking all the bytes and writing them out
        try:
            fd = open(destination,'wb')
            fd.write(file_buffer)
        
            
            # checking we actually wrote the file out
            client_socket.send('File has been successfully saved to {}'.format(destination).encode())        
        except:
            client_socket.send('Failed to save file'.encode())
    
    # check for command execution
    if len(execute):
        print('Execute Sequence active')
        # run command
        output = run_command(execute.encode())
        client_socket.send(output)
    
    # another loop to check if a command shell is needed by client
    if command:
        print('command shell sequence active')
        while True:
            client_socket.send('shell:##'.encode())
            cmd_buffer = ''.encode()
            while '\n'.encode() not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)
            
            response = run_command(cmd_buffer)
            client_socket.send(response)

def client_side(data, target, port):
    'functions to handle client to send and receive data'
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client.connect((target,port))
    #checking if we received anything from stdin
    if len(data):
        print('data received from input..sending to server')
        client.send(data)
    while True:
        recv_len = 1
        response = ''.encode()
        while recv_len:
            data_server = client.recv(4096)
            recv_len = len(data_server)
            response+=data_server
            
            if recv_len < 4096:
                break
        print(response)
        
        #wait for input
        data = input('...')
        data+= '\n'
        
        # send the input
        client.send(data.encode())

def server_side(target, port, destination, execute, command):
    'function to handle command execution and command shell'
    if not len(target):
        print('Target not provided..Exiting')
        target = "0.0.0.0"
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5) 
    print('Server is listening on {}:{} address'.format(target, port))
    
    while True:
        client,addr = server.accept()
        print('Connection accepted from:%s:%d' %(addr[0],addr[1]))
        
        # spinning  up our client thread to handle incoming data
        client_handler = threading.Thread(target=handle_client, args=(client,addr,destination,execute,command))
        client_handler.start()

def run_command(command):
    'function to handle command execution'
    # striping off the newline 
    command = command.rstrip()
    #run the command and getting output back
    
    try:
        output = subprocess.check_output(command.decode(),stderr=subprocess.STDOUT, shell=True)
    except Exception as e:
        print(e)
        output = 'Failed to execute command'
    
    # send the output back to the client
    return output # send the output back to the client

def main():
    'main function'
    listen = False
    port = 0
    execute = ''
    target = ''
    destination = ''
    command = False
    upload = False

    argument_list = sys.argv[1:]
    if not len(argument_list):
        usage()
    
    # reading the commandline options
    short_options = 'hl:e:t:p:cu:'
    long_options = ['help','listen','execute=','target=','port=','command','upload']

    try:
        arguments, values = getopt.getopt(argument_list, short_options, long_options)
    except getopt.error as err:
        print(str(err))
        sys.exit(2)

    # evaluating the given options
    for current_argument, current_value in arguments:
        if current_argument in ('-h', '--help'):
            usage()
        elif current_argument in ('-l', '--listen'):
            listen = True
            target = current_value
        elif current_argument in ('-e', '--execute'):
            execute = current_value
        elif current_argument in ('-u', '--upload'):
            upload = True
            destination  = current_value
            print(destination)
        elif current_argument in ('-c', '--commandshell'):
            command = True
            print('command found')
        elif current_argument in ('-t', '--target'):
            target = current_value
        elif current_argument in ('-p', '--port'):
            port  = int(current_value)
        else:
            assert False , 'Wrong option'

        if not listen and len(target) and port > 0:
            buffer = sys.stdin.read()
            client_side(buffer,target,port)
        
        if listen:
            server_side(target, port,destination, execute, command)

main()