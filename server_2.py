#!/usr/bin/env python
##########################################################################
# Server Script for haramain2 database (layout 2)
##########################################################################
import socket
import pymysql, DBhelper

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
	
def getData(sock):
	phrase = getChunk(sc)
	devID = getChunk(sc)
	time = getChunk(sc)
	lat = getChunk(sc)
	lon = getChunk(sc)
	return (phrase, devID, time, lat, lon)
	
	
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
	try:
		# try getting message from client
		(phrase, devID, time, lat, lon) = getData(sc)
		print 'Passphrase: ', phrase
		print 'Device ID: ', devID
		
		#connect to the DB
		conn = pymysql.connect(host='127.0.0.1', user='haidar', passwd='pin101', db='haramain2')
		cur = conn.cursor()
		
		#check if node has been seen before	
		(nID, session) = DBhelper.findNID_SessionbyDevID(cur, devID)
		
		#if node has not been seen before
		if nID == -1:
			#create a new node keyed by client's passphrase (later; for now, use session1)
			session = 'session1'
			nID = DBhelper.insertNodeInSession(cur, devID, session)
		
		#print Location & Time info
		print 'Time: ', time
		print 'Lattitude: ', lat
		print 'Longitude: ', lon
		#write the location data to DB
		LID = DBhelper.insertLocationInSession(cur, session, nID, time, lat, lon)
		cur.close()
		conn.close()
	except EOFError:
		print "Client closed connection"
	sc.close()
	print 'Socket closed'