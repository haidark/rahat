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
			raise EOFError('socket closed %d bytes into a %d-byte message'
			% (len(data), length))
		data += more
	return data
	
def getChunk(sock):
	len = int(recv_all(sock, 2))
	chunk = recv_all(sock, len)
	if len == 99 and chunk.endswith('~'):
		chunk = chunk.rstrip('~') + getChunk(sock)
	return chunk
	
	
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
	
	# get passphrase and devID from client
	phrase = getChunk(sc)
	print 'Passphrase: ', phrase
	devID = getChunk(sc)
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
	
	#get location info
	time = getChunk(sc)
	print 'Time: ', time
	lat = getChunk(sc)
	print 'Lattitude: ', lat
	lon = getChunk(sc)
	print 'Longitude: ', lon
	#write the location data to DB
	LID = DBhelper.insertLocationInSession(cur, session, nID, time, lat, lon)

	cur.close()
	conn.close()
	sc.close()
	print 'Socket closed'
