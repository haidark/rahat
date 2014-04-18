#!/usr/bin/env python

import socket, sys
import pymysql


def findSIDbyPhrase(cur, phrase):	
	query = "SELECT SID FROM sessions WHERE phrase=%s"
	count = cur.execute(query, phrase)
	if count == 1:
		SID = cur.fetchall()[0]
	else:
		print "Unique session not found for this phrase!!!!!"
		SID = -1	
	return SID
	
def findNIDbyInfo(cur, info):
	query = "SELECT NID FROM nodes WHERE info=%s"
	count = cur.execute(query, info)
	if count == 1:
		NID = cur.fetchall()[0]
	else:
		print "Unique node not found for this info!!!!!"
		NID = -1
	return NID

def insertNode(cur, SID, info):
	query = "INSERT INTO nodes VALUES (NULL, %d, %s)"
	cur.execute(query, (SID, info))
	#just in case
	cur.connection.commit()
	NID = cur.lastrowid
	if NID == None:
		print "Unable to insert new node!!!"
		NID = -1
	return NID
	
def insertLocation(cur, NID, time lat, lon):
	query = "INSERT INTO locations VALUES (NULL, %d, %s, %s, %s)"
	cur.execute(query, (NID, time, lat, lon))
	#just in case
	cur.connection.commit()
	LID = cur.lastrowid
	if LID == None:
		print "Unable to insert new node!!!"
		LID = -1
	return LID

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
HOST = sys.argv.pop() if len(sys.argv) == 2 else '127.0.0.1'
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
	message = recv_all(sc, 6)
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
