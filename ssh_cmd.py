'''Pivoting with BHNET is pretty handy, but sometimes it’s wise to encrypt your traffic to avoid
detection. A common means of doing so is to tunnel the traffic using Secure Shell (SSH). But what if
your target doesn’t have an SSH client'''

# importing packages
import paramiko
import threading
import subprocess

def ssh_command(ip, user, passwd, command):
    'function to connect to an ssh server and run a single command'
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=user, password=passwd)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.exec_command(command)
        print(ssh_session.recv(1024))
    return

#ssh_command('192.168.43.105', 'anonymous', 'claudia', 'ls')
