#!/usr/bin/env python
##########################################################################
# Server Script for haramain2 database (layout 2)
##########################################################################
import socket
import pymysql, DBhelper
import thread

def recv_all(sock, length):
	data = ''
	while len(data) < length:
		more = sock.recv(length - len(data))
		if not more:
			raise EOFError('socket closed %d bytes into a %d-byte message' % (len(data), length))
		data += more
	return data
	
def getChunk(sock):
	len = int(recv_all(sock, 2))
	chunk = recv_all(sock, len)
	if len == 99 and chunk.endswith('~'):
		chunk = chunk.rstrip('~') + getChunk(sock)
	return chunk
	
def handleClient(clientSock, addr):
	try:
		# get data from client
		(phrase, devID, time, lat, lon) = getData(clientSock)
		# get phrase from client
		phrase = getChunk(clientSock)
		
		#connect to the DB
		conn = pymysql.connect(host='127.0.0.1', user='haidar', passwd='pin101', db='haramain2')
		cur = conn.cursor()
		
		#get devID from client
		devID = getChunk(clientSock)
		#check if node has been seen before	
		(nID, session) = DBhelper.findNID_SessionbyDevID(cur, devID)
		
		#if node has not been seen before
		if nID == -1:
			#create a new node keyed by client's passphrase (later; for now, use session1)
			session = 'session1'
			nID = DBhelper.insertNodeInSession(cur, devID, session)
		time = getChunk(clientSock)
		lat = getChunk(clientSock)
		lon = getChunk(clientSock)
		#write the location data to DB
		LID = DBhelper.insertLocationInSession(cur, session, nID, time, lat, lon)
		cur.close()
		conn.close()
		print "(+) Received data from %s" % devID
	except EOFError:
		print "(-) Client %s closed connection" %addr
	clientSock.close()
	print "\t(=) Connection with %s closed" % addr
	
#start server code	
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = '192.168.1.222'
PORT = 1060

s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(5)
while True:
	print '\t(=) Listening at', s.getsockname()
	clientSock, sockname = s.accept()
	print "(+) Connected to %s established" % sockname
	handleClient(clientSock)