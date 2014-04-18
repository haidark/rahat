#!/usr/bin/env python

import socket, sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = sys.argv.pop() if len(sys.argv) == 2 else '127.0.0.1'
PORT = 1060

def recv_all(sock, length):
	data = ''
	while len(data) < length:
		more = sock.recv(length - len(data))
		if not more:
			raise EOFError('socket closed %d bytes into a %d-byte message'
			% (len(data), length))
		data += more
	return data

s.connect((HOST, PORT))
print 'Client has been assigned socket name', s.getsockname()
s.sendall('session1')
s.sendall('-120')
s.sendall('1234')
s.sendall('1991-11-04')
print 'Location info sent'
s.close()