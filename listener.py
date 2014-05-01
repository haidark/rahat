import pymysql
import socket
from DBhelper import getNode, createLocation, NodeError
from threading import Thread
#----------------------------------------------------------------------------------------------#
class Listener(Thread):
	"""Listener Class - inherits from threading.Thread
		Static Members:
			DBINFO tuple which containt database information - (host, user, pass, db)
		Members:
			host - Host IP address to listen on - string "xxx.xxx.xxx.xxx"
			port - Port number to listen on - int > 1000
		
		Functions:
			implements theading.Thread.run() - can be multi threaded
			run() - socket code to bind to (IP, port) and accepts all clients
					spawns client thread to handle clients
	"""
	
	def __init__(self, host, port):
		Thread.__init__(self)
		self.host = host
		self.port = port

	DBINFO = ('192.168.1.222', 'haidar', 'pin101', 'haramain2')
	
	def run(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind((self.host, self.port))
		s.listen(5)
		while True:
			print '\t(=) Listening at', s.getsockname()
			clientSock, sockname = s.accept()
			print "(+) Connected to %s established" % str(sockname)
			#multi-threaded
			clientThread = ClientHandlerThread(clientSock, DBINFO)
			clientThread.start()
#----------------------------------------------------------------------------------------------#
class ClientHandlerThread(Thread):
	"""ClientHandlerThread Class - inherits from threading.Thread
		Static Members:
			None
		Members:
			cSock - socket which holds client connection - socket
			dbHost - Host IP upon which the DB resides
			dbUser - Database User - needs SELECT/INSERT privileges
			dbPass - Password for Database User
			dbDb - Name of database on Database
		
		Functions:
			implements theading.Thread.run() - can be multi threaded
			run() - gets location info from client, handles all errors
					if valid data, writes it to the DB
					
			recv_all(sock, length) - blocking call to receive length bytes from client, returns length bytes
			getChunk - gets data formatted with data length in first two bytes, returns data string
	"""
	
	def __init__(self, clientSock, dbInfo):
		Thread.__init__(self)
		self.cSock = clientSock
		self.dbHost = dbInfo[0]
		self.dbUser = dbInfo[1]
		self.dbPass = dbInfo[2]
		self.dbDb = dbInfo[3]
		
	def run(self):
		try:
			#connect to the DB
			conn = pymysql.connect(self.dbHost, self.dbUser, self.dbPass, self.dbDb)
			cur = conn.cursor()
			
			# get phrase from client - going to remove this, client only needs to send deviceID
			phrase = getChunk()		
			
			#get devID from client
			devID = getChunk()		
			
			#check if node exists
			try:
				node = getNode(cur, devID)
				nID = node[0]
				session = node[2]
				if session == None:
					print "(-) Node is not active. Device ID: %s" % devID
				else:
					time = getChunk()
					lat = getChunk()
					lon = getChunk()
					#write the location data to DB
					LID = createLocation(cur, session, nID, time, lat, lon)
					print "(+) Received data. Device ID: %s" % devID
			#if the node does not exist
			except NodeError:
				print "(-) Device not recognized. Device ID: %s" % devID			
		# if client hangs up
		except EOFError:
			print "(-) Client %s closed connection" % str(self.cSock.getsockName())
		cur.close()
		conn.close()	
		self.cSock.close()
		print "\t(=) Connection with %s closed" % str(self.cSock.getsockName())
		
	def recv_all(sock, length):
		data = ''
		while len(data) < length:
			more = sock.recv(length - len(data))
			if not more:
				raise EOFError('socket closed %d bytes into a %d-byte message' % (len(data), length))
			data += more
		return data
	
	def getChunk():
		len = int(recv_all(self.cSock, 2))
		chunk = recv_all(self.cSock, len)
		if len == 99 and chunk.endswith('~'):
			chunk = chunk.rstrip('~') + getChunk()
		return chunk
#----------------------------------------------------------------------------------------------#
if __name__=="__main__":
	t = Listener('192.168.1.222', 1060)
	t.run()
