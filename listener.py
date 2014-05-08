import socket
import time
import logging
from DBManager import DBManager, NodeError
from threading import Thread
from multiprocessing import Process
#----------------------------------------------------------------------------------------------#
class Listener(Process):
	"""Listener Class - inherits from multiprocessing.Process
		Static Members:
			None
		Members:
			listenSock - bound socket which can be listened on from multiple listeners
			listenerID - Identifier for this listener		
		Functions:
			implements multiprocessing.Process.run() - can be multi process
			run() - socket code to bind to (IP, port) and accepts all clients
					spawns client thread to handle clients
	"""
	
	def __init__(self, listenSock, listenerID):
		Process.__init__(self)
		self.listenSock  = listenSock
		self.listenerID = listenerID
		logging.basicConfig(filename='listener.log', format='%(levelname)s:%(message)s', level=logging.INFO)
	
	def run(self):
		self.listenSock.listen(5)
		#main server loop
		while True:
			clientSock, sockname = self.listenSock.accept()
			#multi-threaded client handler
			clientThread = ClientHandlerThread(clientSock, sockname, 15, self.listenerID)
			clientThread.start()
#----------------------------------------------------------------------------------------------#
class ClientHandlerThread(Thread):
	"""ClientHandlerThread Class - inherits from threading.Thread
		Static Members:
			None
		Members:
			cSock - socket which holds client connection - socket
			sockname - name assigned to remote socket
			timeout - time in seconds before connection is dropped due to inactivity
			parentID - parent listener identifier
		Functions:
			implements threading.Thread.run() - can be multi threaded
			run() - gets location info from client, handles all errors
					if valid data, writes it to the DB
					
			recv_all(sock, length) - blocking call to receive length bytes from client, returns length bytes
			getChunk() - gets data formatted with data length in first two bytes, returns data string
	"""
	
	
	def __init__(self, clientSock, clientAddr, timeout, parentID):
		Thread.__init__(self)
		self.cSock = clientSock
		self.cSock.settimeout(timeout)
		self.sockname = str(clientAddr)
		self.parentID = parentID
		
	def run(self):
		try:
			logMsg = 'Place holder for log message'
			#get current time
			now = time.strftime("%m/%d/%Y %H:%M:%S")
			#prepend parent ID to time string
			now = str(self.parentID) + " " + now
			#connect to the database by constructing a DBManager object
			db = DBManager()
			#get devID from client
			devID = self.getChunk()		
			
			#check if node exists
			try:
				node = db.getNode(devID)
				nID = node[0]
				
				#get the location time and data from the client
				locTime = self.getChunk()
				lat = self.getChunk()
				lon = self.getChunk()
				
				#update node location in nodes table regardless of whether it is active
				db.updateNodeLocation(nID, locTime, lat, lon)
				tblName = node[2]
				if tblName == None:
					logMsg = "(-) %s: Node at %s is not active. Device ID: %s" % (now, self.sockname, devID)
				else:
					#write the location data to DB
					db.createLocation(tblName, nID, locTime, lat, lon)
					logMsg = "(+) %s: Received data from %s. Device ID: %s" % (now, self.sockname, devID)
			#if the node does not exist
			except NodeError:
				logMsg = "(-) %s: Device at %s not recognized. Device ID: %s" % (now, self.sockname, devID)
		# if client hangs up
		except (EOFError, socket.timeout):
			logMsg = "(-) %s: Client %s closed connection or timed-out" % (now, self.sockname)

		logging.info(logMsg)
		print logMsg
		db.close()
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
	
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind(('192.168.1.222', 1060))
	
	t1 = Listener(sock, 1)
	t2 = Listener(sock, 2)
	t1.start()
	t2.start()
	while True:
		pass
