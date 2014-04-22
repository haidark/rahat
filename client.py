#!/usr/bin/env python

def preLen(string):
	#prepends length of the string to the string.
	#if length of string is more than 99 characters, the string is sent piecemeal
	if len(string) <= 99:
		return str(len(string))+string
	else:
		return str(99)+string[0:98]+'~'+preLen(string[98:])

import socket, sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = '192.168.1.222'
PORT = 1060


s.connect((HOST, PORT))
print 'Client has been assigned socket name', s.getsockname()
phrase = 'session1'
devID = 'python-script'
time = '1991-09-04'
lat = '-12.2111'
lon = '123.41234'

msg = preLen(phrase)+ preLen(devID) + preLen(time) + preLen(lat) + preLen(lon)
s.sendall(msg) 
print 'Location info sent'
s.close()