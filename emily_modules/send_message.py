import socket
import sys

def send(message):
    s = socket.socket()
    port = 8000
    s.connect(('127.0.0.1',port))
    s.send(message)
    response = s.recv(4096)
    s.close()
    # print(response)
    return response

if __name__ == '__main__':
    send(sys.argv[1])