#!/usr/bin/env python
##########################################################################
# Python Client script
##########################################################################
def preLen(string):
	#prepends length of the string to the string.
	
	#if length is less than 10, pad with leading zero
	if len(string) < 10:
		length = '0' + str(len(string))
	else:
		length = str(len(string))
	
	#if length of string is more than 99 characters, the string is sent piecemeal
	if len(string) <= 99:
		return length+string
	else:
		return str(99)+string[0:98]+'~'+preLen(string[98:])

import socket, sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = 'haidarkhan.no-ip.org'
PORT = 1060


s.connect((HOST, PORT))
print 'Client has been assigned socket name', s.getsockname()
devID = 'python-script'
time = '1991-09-04 12:25:49'
lat = '-12.2111'
lon = '123.41234'

msg = preLen(devID) + preLen(time) + preLen(lat) + preLen(lon)
s.sendall(msg) 
print 'Location info sent'
s.closed()