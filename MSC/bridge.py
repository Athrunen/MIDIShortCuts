from socket import *



def open_listener():
    bclistener = socket(AF_INET, SOCK_DGRAM)
    bclistener.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    bclistener.bind(('0.0.0.0', 24444))
    return bclistener

def await_controller(bclistener):
    while True:
        message = bclistener.recvfrom(64)
        if (message[0] == b'ThatLEDController online!'):
            return message[1][0]

def open_sender(ip):
    cmsender = socket(AF_INET, SOCK_STREAM)
    cmsender.connect((ip, 25555))
    return cmsender

def send_command(socket, command, options):
    socket.send(f"{command} {' '.join(str(x) for x in options)} \n".encode("utf-8"))

