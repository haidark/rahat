import pymysql
import socket
import time
from DBhelper import getNode, createLocation, NodeError
from threading import Thread
from multiprocessing import Process
#----------------------------------------------------------------------------------------------#
class Listener(Process):
	"""Listener Class - inherits from multiprocessing.Process
		Static Members:
			DBINFO tuple which contains database information - (host, user, pass, db)
		Members:
			host - Host IP address to listen on - string "xxx.xxx.xxx.xxx"
			port - Port number to listen on - int > 1000
		
		Functions:
			implements multiprocessing.Process.run() - can be multi process
			run() - socket code to bind to (IP, port) and accepts all clients
					spawns client thread to handle clients
	"""
	
	def __init__(self, host, port):
		Process.__init__(self)
		self.host = host
		self.port = port
	
	DBINFO = ('127.0.0.1', 'haidar', 'pin101', 'haramain2')
	
	def run(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind((self.host, self.port))
		s.listen(5)
		while True:
			clientSock, sockname = s.accept()
			#multi-threaded
			clientThread = ClientHandlerThread(clientSock, sockname, Listener.DBINFO)
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
			implements threading.Thread.run() - can be multi threaded
			run() - gets location info from client, handles all errors
					if valid data, writes it to the DB
					
			recv_all(sock, length) - blocking call to receive length bytes from client, returns length bytes
			getChunk - gets data formatted with data length in first two bytes, returns data string
	"""
	
	def __init__(self, clientSock, clientAddr, dbInfo):
		Thread.__init__(self)
		self.cSock = clientSock
		self.sockname = str(clientAddr)
		self.dbHost = dbInfo[0]
		self.dbUser = dbInfo[1]
		self.dbPass = dbInfo[2]
		self.dbDb = dbInfo[3]
		
	def run(self):
		try:
			#get current time
			now = time.strftime("%m/%d/%Y %H:%M:%S")
			#connect to the DB
			conn = pymysql.connect(self.dbHost, self.dbUser, self.dbPass, self.dbDb)
			cur = conn.cursor()
			
			#get devID from client
			devID = self.getChunk()		
			
			#check if node exists
			try:
				node = getNode(cur, devID)
				nID = node[0]
				session = node[2]
				if session == None:
					print "(-) %s: Node is not active. Device ID: %s" % now, devID
				else:
					time = self.getChunk()
					lat = self.getChunk()
					lon = self.getChunk()
					#write the location data to DB
					LID = createLocation(cur, session, nID, time, lat, lon)
					print "(+) %s: Received data. Device ID: %s" % now, devID
			#if the node does not exist
			except NodeError:
				print "(-) %s: Device not recognized. Device ID: %s" % now, devID			
		# if client hangs up
		except EOFError:
			print "(-) %s: Client %s closed connection" % now, str(self.sockname)
		cur.close()
		conn.close()	
		self.cSock.close()
		
	def recv_all(self, length):
		data = ''
		while len(data) < length:
			more = self.cSock.recv(length - len(data))
			if not more:
				raise EOFError('(-) Socket closed %d bytes into a %d-byte message' % (len(data), length))
			data += more
		return data
	
	def getChunk(self):
		len = int(self.recv_all(2))
		chunk = self.recv_all(len)
		if len == 99 and chunk.endswith('~'):
			chunk = chunk.rstrip('~') + getChunk()
		return chunk
#----------------------------------------------------------------------------------------------#
if __name__=="__main__":
	t = Listener('192.168.1.222', 1060)
	t.run()
