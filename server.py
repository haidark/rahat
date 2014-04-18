#!/usr/bin/env python

import socket
import pymysql, DBhelper

def recv_all(sock, length):
	data = ''
	while len(data) < length:
		more = sock.recv(length - len(data))
		if not more:
			raise EOFError('socket closed %d bytes into a %d-byte message'
			% (len(data), length))
		data += more
	return data
	
#start server code	
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = '192.168.1.222'
PORT = 1060

s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(1)
while True:
	print 'Listening at', s.getsockname()
	sc, sockname = s.accept()
	#connect to the DB
	conn = pymysql.connect(host='127.0.0.1', user='haidar', passwd='pin101', db='haramain')
	cur = conn.cursor()
	
	print 'We have accepted a connection from', sockname
	print 'Socket connects', sc.getsockname(), 'and', sc.getpeername()
	# get passphrase from client
	message = recv_all(sc, 8)
	print 'The passphrase is', repr(message)
	#search database for phrase
	SID = findSIDbyPhrase(cur, message)
	#if SID exists	
	if  SID != -1:
		#check if node has been seen before
		info = str(sc.getpeername()[0])
		NID = findNIDbyInfo(cur, info)
		#if node has not been seen before
		if NID == -1:
			#create a new node
			NID = insertNode(cur, SID, info)
		
		#get location info
		lat = recv_all(sc, 4)
		lon = recv_all(sc, 4)
		time = recv_all(sc, 10)		
		#write the location data to DB
		LID = insertLocation(cur, NID, time, lat, lon)
	#if not found, raise an error
	else:
		print "Session not found!!!!\n closing connection..."
	cur.close()
	conn.close()
	sc.close()
	print 'Socket closed'
