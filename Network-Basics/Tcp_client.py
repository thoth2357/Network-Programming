import socket

target_host = '127.1.2.3'
target_port = 5555

#create a client object 
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect the client
client.connect((target_host, target_port))


# send some data
msg = 'hello server'
client.send(msg.encode())

# receive some data
response = client.recv(4096)

print(response)