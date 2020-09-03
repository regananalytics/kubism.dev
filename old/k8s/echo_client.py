#!/usr/bin/env conda run -n kube python

import socket

HOST = '172.24.12.160'
PORT = 8080

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'Hello Server!')
    data = s.recv(1024)

print('Recieved', repr(data))
