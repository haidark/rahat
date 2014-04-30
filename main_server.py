#!/usr/bin/env python
##########################################################################
# Server Script for haramain2 database (layout 2)
##########################################################################
import socket
import pymysql
import thread
from DBhelper import getNode, createLocation, NodeError

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
		#connect to the DB
		conn = pymysql.connect(host='127.0.0.1', user='haidar', passwd='pin101', db='haramain2')
		cur = conn.cursor()
		
		# get phrase from client - going to remove this, client only needs to send deviceID
		phrase = getChunk(clientSock)		
		
		#get devID from client
		devID = getChunk(clientSock)		
		
		#check if node exists
		try:
			node = getNode(cur, devID)
			nID = node[0]
			session = node[2]
			if session == None:
				print "(-) Node is not active. Device ID: %s" % devID
			else:
				time = getChunk(clientSock)
				lat = getChunk(clientSock)
				lon = getChunk(clientSock)
				#write the location data to DB
				LID = createLocation(cur, session, nID, time, lat, lon)
				print "(+) Received data. Device ID: %s" % devID
		#if the node does not exist
		except NodeError:
			print "(-) Device not recognized. Device ID: %s" % devID	
	# if client hangs				
	except EOFError:
		print "(-) Client %s closed connection" % addr
	cur.close()
	conn.close()
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
	print "(+) Connected to %s established" % str(sockname)
	#multi-threaded
	thread.start_new_thread(handleClient, (clientSock, str(sockname)))
	#single process
	#handleClient(clientSock, str(sockname))