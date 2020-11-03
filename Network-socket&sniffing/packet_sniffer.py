# importing packages
import socket
import os

# host to listen on
host = '192.168.43.105 '

'''Constructing  a socket object with the parameters needed for sniffing packets on out network'''
'''The difference between Windows and Linux is that Windows will allow us to
sniff all incoming packets regardless of protocol, whereas Linux forces us to specify that we are
sniffing ICMP'''

#create a raw socket and bind it to the public interface
if os.name == 'nt':
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
sniffer.bind((host, 0))

# we want the ip header included in the capture
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# if we using windows, we need to send an IOCTL to set up promiscuos mode
if os.name == 'nt':
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

# read in a single packet
print(sniffer.recvfrom(65565))

# we using windows, turn off promsicuous mode
if os.name == 'nt':
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)


