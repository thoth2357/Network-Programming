#importing packages
import socket
import threading

# binding the address of the server
bind_ip = "127.1.2.3"
bind_port = 5555

# creating the server socket object
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# binding the address we want the server to listen on
server.bind((bind_ip, bind_port))

# opening our server to listen for connections
server.listen(5) # this is a backlog connection of 5 connections

print('Server is listening on {}:{} address'.format(bind_ip, bind_port))

# client handling thread
def handle_client(client_socket,addr):
    'function to handle respective clients needs'
    request = client_socket.recv(1024) #prints out the data the client sends
    print('Server received {} from {}'.format(request, addr))
    
    #send back a packet
    msg = 'ACK!'
    client_socket.send(msg.encode())
    
    client_socket.close()
    
while True:
    client,addr = server.accept() #initializing the variable to hold the client received by the server
    print('Connection accepted from:%s:%d' %(addr[0],addr[1]))
    
    # spinning  up our client thread to handle incoming data
    client_handler = threading.Thread(target=handle_client, args=(client,addr))
    client_handler.start()