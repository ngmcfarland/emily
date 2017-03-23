import socket
import json
import sys

def send(message,session_id,port=8000):
    s = socket.socket()
    s.connect(('127.0.0.1',port))
    s.send(json.dumps({'message':message,'session_id':session_id}).encode())
    s_response = s.recv(4096)
    s_response = json.loads(s_response.decode())
    s.close()
    return s_response['response'],s_response['session_id']

if __name__ == '__main__':
    send(sys.argv[1])