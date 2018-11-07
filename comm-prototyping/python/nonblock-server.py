import sys
import socket
import fcntl, os
import errno
from time import sleep
import signal


server = None

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    print("-" * 20)
    print("Shutting down...")
    server.close()
    os.remove("/tmp/python_unix_sockets_example")
    print("Done")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def init(socket_path):
    if os.path.exists(socket_path):
        os.remove(socket_path)
    print("Opening socket...")
    server = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    server.bind(socket_path)
    fcntl.fcntl(server, fcntl.F_SETFL, os.O_NONBLOCK)
    return server

def get_data(server):
    try:
        datagram = server.recv(1024)
    except socket.error, e:
        err = e.args[0]
        if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
            sleep(1)
            #print 'No data available'
            return 0,''
        else:
            # a "real" error occurred
            print e
            sys.exit(1)
    else:
        if not datagram:
            return -1, ''
        else:
            strback = datagram.decode('utf-8')
            #print(strback)
            if "DONE" == strback:
                return -1, ''
            return len(strback),strback

server = init('/tmp/python_unix_sockets_example')


def followball(newpos):
    pos = newpos.split(',')
    if (len(pos) == 3):
        print (pos[0])
        print (pos[1])
        print (pos[2])        
        rho = float(pos[1])
        theta = int(pos[2])
        print "rho %s theta %s " % (rho,theta)        


while True:
    succode, strback = get_data(server)
    if (succode == 0):
        print ('.'),
        sys.stdout.flush()        
    if (succode > 0):
        print (strback.rstrip())
        followball(strback.rstrip())
    if succode < 0:
        break


print("-" * 20)
print("Shutting down...")
server.close()
os.remove("/tmp/python_unix_sockets_example")
print("Done")
