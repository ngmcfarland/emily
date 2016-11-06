import threading
import socket
import sys


class MySocket(threading.Thread):
    """docstring for MySocket"""
    def __init__(self):
        super(MySocket, self).__init__()
        self.s = socket.socket()
        self.s.bind(('',8000))
        self.s.listen(5)

    def run(self):
        while True:
            c,addr = self.s.accept()
            user_input = c.recv(4096)
            response = "You entered: {}".format(user_input)
            c.send(response)
            c.close()
            if user_input.upper() in ['Q','QUIT','EXIT','BYE']:
                self.s.close()
                break

    def send(self,message):
        new_s = socket.socket()
        port = 8000
        new_s.connect(('localhost',port))
        new_s.send(message)
        response = new_s.recv(4096)
        new_s.close()
        # print(response)
        return response
        

"""
def server():
    s = socket.socket()
    s.bind(('',8000))
    s.listen(5)
    
    while True:
        c,addr = s.accept()
        user_input = c.recv(4096)
        response = "You entered: {}".format(user_input)
        c.send(response)
        c.close()
        if user_input.upper() in ['Q','QUIT','EXIT','BYE']:
            s.close()
            break

threads = []
t = threading.Thread(target=server)
threads.append(t)
t.start()

def send(message):
    new_s = socket.socket()
    port = 8000
    new_s.connect(('127.0.0.1',port))
    new_s.send(message)
    response = new_s.recv(4096)
    new_s.close()
    # print(response)
    return response
"""