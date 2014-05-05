import pymysql

class DBManager:
	"""DBManager class holds functions to carry out actions on the database 
	while maintaining integrity of the data
	
	to construct a new DBManager, pass the constructor a tuple containing database login info:
		db = DBManager((host, user, password, db))
		
	use db.close() to free its resources
	"""
	def __init__(self, info):
		#connect to the DB
		self.conn = pymysql.connect(host=info[0], user=info[1], passwd=info[2], db=info[3])
		self.cur = conn.cursor()
		
	def close(self):
		self.conn.close()
		self.cur.close()
		
	"""SESSION FUNCTIONS"""
	def createSession(self, session):
		#creates a new table titled by the session phrase.
		#raises a SessionError if table with same name already exists
		#5 columns: lID, nodeID, time, lat, lon
		if self.SessionExists(session):
			raise SessionError(session, SessionError.AE)
		else:
			cols = "(lID INT NOT NULL AUTO_INCREMENT, nodeID INT NOT NULL, time DATETIME, lat FLOAT, lon FLOAT, PRIMARY KEY(lID))"
			query = "CREATE TABLE IF NOT EXISTS %s " + cols
			self.cur.execute(query % session)
			self.cur.connection.commit()
			return
	
	def deleteSession(self, session):
		#drops the table associated with a session
		if self.SessionExists(session):
			self.cur.execute("DROP TABLE " + str(session))
			self.cur.connection.commit()
		else:
			raise SessionError(session, SessionError.DNE)
	
	def SessionExists(self, session):
		#checks if a session exists, boolean function
		#returns 1 if session exists and 0 if it does not
		return self.cur.execute("SHOW TABLES LIKE %s", session)
		
	"""NODE FUNCTIONS"""	
	def createNode(self, devID, session=None):
		#creates a new node in the "nodes" table
		#the session it belongs to is optional and defaulted to NULL
		#returns the nID if the node was created or found in the table
		
		#check if the node already exists
		try:
			node = self.getNode(devID)
			return node[0]
		#if the node does not exist
		except NodeError as ne:		
			if ne.msg == NodeError.DNE:
				#if user specifies a session and it does not exist
				if session != None and not self.SessionExists(session):
					#raise a session does not exist error
					raise SessionError(session, SessionError.DNE)
				#otherwise proceed as normal
				else:
					query = "INSERT INTO nodes VALUES (NULL, %s, %s)"
					self.cur.execute(query, (devID, session))	
					self.cur.connection.commit()
					#get the node ID
					nID = self.cur.lastrowid
					return nID
	
	def deleteNode(self, devID):
		#Removes the given node from the table of nodes
		#if the node is active, removes all the rows associated with the node in its session table	
		
		#check if node exists, raises NodeError if it does not exist
		node = self.getNode(devID)
		nID = node[0]
		session = node[2]
		#check if node is active
		if session != None:
			#delete all rows in its session table associated with its nID
			self.cur.execute("DELETE FROM " + str(session) + " WHERE nodeID=%s", nID) 
		#now delete it from the nodes table
		self.cur.execute("DELETE FROM nodes WHERE devID=%s", devID)
		self.cur.connection.commit()
	
	def activateNode(self, devID, session):
		#changes the session of a node to the new session iff the node exists AND is a free node
		
		#if the node does not exist or it is already in a session, raises a NodeError
		self.assertFreeNode(self.getNode(devID))
		#if the specified session does not exist, raise a SessionError
		if not self.SessionExists(session):
			raise SessionError(session, SessionError.DNE)
		else:
		#if all is well(no errors raised)
			query = "UPDATE nodes SET session=%s WHERE devID=%s"
			count = self.cur.execute(query, (session, devID))
			self.cur.connection.commit()
			return
			
	def freeNode(self, devID):
		#changes the session column of a node to NULL
		query = "UPDATE nodes set session=NULL WHERE devID=%s"
		count = self.cur.execute(query, devID)
		self.cur.connection.commit()
		#if something goes wrong
		if count == 0:
			#check if node exists or node was already free
			self.checkNodeState(self.getNode(devID))
		else:
			return
	
	def getNode(self, devID):
		#gets a node from the nodes table and returns the whole row
		#raises a NodeError if the node does not exist
		nodeExists = self.cur.execute("Select * from nodes WHERE devID=%s", devID)
		if nodeExists == 0:
			raise NodeError(devID, NodeError.DNE)
		else:
			return self.cur.fetchone()
			
	def assertFreeNode(self, node):
		#if node is not free raise NodeError
		if node[2] != None:
			raise NodeError(node[1], NodeError.ACT)
		else:
			return node
			
	def assertActiveNode(self, node):
		#if node is free raise NodeError	
		if node[2] == None:
			raise NodeError(node[1], NodeError.FRE)
		else:
			return node
			
	def checkNodeState(self, node):
		#checks why
		#if node is not free raise Active NodeError
		if node[2] != None:
			raise NodeError(node[1], NodeError.ACT)
		#if the node is free raise Free NodeError
		else:
			raise NodeError(node[1], NodeError.FRE)
			
	"""LOCATION FUNCTIONS"""	
	def createLocation(self, session, nID, time, lat, lon):
		if not self.SessionExists(cur, session):
			raise SessionError(session, SessionError.DNE)
		else:
			query = "INSERT INTO {0} VALUES (NULL, %s, %s, %s, %s)".format(session)
			self.cur.execute(query, (nID, time, lat, lon))
			self.cur.connection.commit()
			lID = self.cur.lastrowid
			return lID

	"""DISPLAY FUNCTIONS"""
	def displaySessions(self):
		#displays a list of all active sessions
		self.cur.execute("SHOW TABLES")
		sessions = self.cur.fetchall()
		for session in sessions:
			print "\t", session		
	
	def displayNodes(self, session=0):
		#displays a list of all nodes
		if session == 0:
			self.cur.execute("SELECT * FROM nodes")
		else:
			self.cur.execute("SELECT * FROM nodes WHERE session=%s", session)
		nodes = self.cur.fetchall()
		for node in nodes:
			print "\t", node

##########################################################################
##########################################################################
##################### Exception Definitions ##############################
##########################################################################
##########################################################################

class Error(Exception):
	"""Base class for exceptions in this module."""
	pass
	
class NodeError(Error):
	"""Exception raised for errors related to nodes.

	Attributes:
	devID -- input devID for which node error occurred
	msg  -- explanation of the error
	"""
	
	def __init__(self, devID, msg):
		self.devID = devID
		self.msg = msg
	
	#Error Types
	DNE = "Node Does Not Exist"
	AE = "Node Already Exists"
	ACT = "Node is Active"
	FRE = "Node is Free"
	
class SessionError(Error):
	"""Exception raised for errors related to sessions.

	Attributes:
	session -- input session for which session error occurred
	msg  -- explanation of the error
	"""	
	
	def __init__(self, session, msg):
		self.session = session
		self.msg = msg
	
	#Error types
	DNE = "Session Does Not Exist"
	AE = "Session Already Exists"
		
class FieldError(Error):
	"""Exception raised for errors related to invalid fields.

	Attributes:
	field -- input field for which field error occurred
	msg  -- explanation of the error
	"""
	
	def __init__(self, field, msg):
		self.field = field
		self.msg = msg
	
	#Error types
	IP = "Invalid Phrase for Session"
	ID = "Invalid devID for Node"
		
