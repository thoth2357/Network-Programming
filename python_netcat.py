# importing packages
import socket
import sys
import threading 
import getopt
import subprocess

#defining some gloval variables
listen = False
command = False
upload = False
execute = ''
target = ''
port = 0
upload_destination = ''

#functions for handling command line arguments
def usage():
    print('Net tool\n')
    print('Usage;python_netcat.py -t target_host -p port')
    print('Options')
    print('-l --listen\t\t-listen on [host]:[port] for incoming connections')
    print('-e --execute-\t\t-execute the given file upon receiving a connection')
    print('-u --upload-destination\t\t -upon receiving connection upload a file and write to [destination]\n\n\n')

    print('Examples')
    print('python_netcat.py -t 127.0.0.1 -p 5454 -l -c')
    print('python_netcat.py -t 127.0.0.1 -p 5454 -l -u=c:\\target.exe')
    print('python_netcat.py -t 127.0.0.1 -p 5454 -e=\"cat /etc/passwd\"')
    print('echo "Welcome" | ./python_netcat.py -t 127.0.0.1 -p 80')
    sys.exit(0)
    
def client_sender(buffer):
    'functions to handle client to send and receive data'
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try: #connecting to our target host
        client.connect((target,port))
        if len(buffer):
            client.send(buffer)
        while True:
            recv_len = 1
            response = ''
            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response+=data
                
                if recv_len < 4096:
                    break
            print(response)
            
            #wait for input
            buffer = input('...')
            buffer+= '\n'
            
            # send the input
            client.send(buffer)
    except:
        print('Exception found..Exiting')
        client.close()       

def server_loop():
    'function to handle command execution and command shell'
    global target
    if not len(target): # if target is not defined, we all listen on all interfaces
        target = '0.0.0.0'
    
    # creating server socket object
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # binding server to address given and listening on it
    server.bind((target,port))
    server.listen(5) # backlog connections of 5 maximum
    
    
    

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target
    
    if not len(sys.argv[1:])
        usage()
    
    # reading the commandline options
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hle:t:p:cu",['help','listen','execute','target','port','command','upload'])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
    
    for o,i in opts:
        if o in ('-h', '--help'):
            usage()
        elif o in ('-l', '--listen'):
            listen = 1
        elif o in ('-e', '--execute'):
            execute = 1
        elif o in ('-u', '--upload'):
            upload_destination = i
        elif o in ('-c', '--commandshell'):
            command = 1
        elif o in ('-t', '--target'):
            target = i
        elif o in ('-p', '--port'):
            port = int(a)
        else:
            assert False, "wrong option"
        
        # if we plan on listening or just sending data from stdin only
        if not listen and len(target) and port > 0:
            buffer = sys.stdin.read()
            
        # if we are only planning on listening,uploading things, executing commands and having a shell back
        if listen:
            server_loop()
            
main()

         
            
               



