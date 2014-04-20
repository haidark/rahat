#!/usr/bin/env python

import socket, sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = '192.168.1.222'
PORT = 1060


s.connect((HOST, PORT))
print 'Client has been assigned socket name', s.getsockname()
s.sendall('session1')
s.sendall('-120')
s.sendall('1234')
s.sendall('1991-11-04')
print 'Location info sent'
s.close()