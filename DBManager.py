import pymysql
import datetime

class DBManager:
	"""DBManager class - holds functions to carry out actions on the database 
	while maintaining integrity of the data
	
	To construct a new DBManager, pass the constructor a tuple containing database login info:
		db = DBManager()
	Make sure to use db.close() to free its resources
		Static Members:
			DBINFO tuple which contains database information - (host, user, pass, db)
		Members:
			conn - connection to the database
			cur - cursor for the connection to the database		
		Functions:
			----Database-------------------------------------------------------------------------------------------
			__init__() - connects to database and creates a cursor object
			close() - closes connection to database and closes cursor object
			
			----Sessions-------------------------------------------------------------------------------------------
			createSession(phrase, duration) - creates a new session if one by the same name DNE TODO error check duraion
			deleteSession(phrase) - deletes a session if it exists and frees all nodes in that session
			getSession(phrase) - gets a session from the sessions table
			getSessions() - gets all sessions in the session table (useful for printing)
			SessionExists(phrase) - returns true if the session exists, false otherwise

			----Nodes----------------------------------------------------------------------------------------------
			createNode(devID) - creates a new node if one by the same name DNE
			deleteNode(devID) - deletes a node and removes any location entries in its current session table
			activateNode(devID, phrase) - adds an existing node to a session
			freeNode(devID) - frees an existing node from its session
			getNode(devID) - gets a node from the nodes table
			getNodes([phrase]) - gets all nodes or all nodes in a session (useful for printing)
			NodeExists(devID) - returns true if the node exists, false otherwise				
			assertFreeNode(devID) - raises an error if the node is not free
			assertActiveNode(devID) - raises an error if the node is free
			checkNodeState(devID) - checks if node is free or active and raises appropriate error

			----Locations------------------------------------------------------------------------------------------
			createLocation(tblName, nID, time, lat, lon) - adds location row to a session table
			updateNodeLocation(nID, time, lat, lon) - updates last known location of node
		
	"""
	DBINFO = ('127.0.0.1', 'haidar', 'pin101', 'haramain2')
	def __init__(self):
		#connect to the DB
		self.conn = pymysql.connect(host=DBManager.DBINFO[0], user=DBManager.DBINFO[1], passwd=DBManager.DBINFO[2], db=DBManager.DBINFO[3])
		self.cur = self.conn.cursor(pymysql.cursors.DictCursor)
		
	def close(self):		
		self.cur.close()
		self.conn.close()
		
	"""SESSION FUNCTIONS"""
	def createSession(self, phrase, days):		
		#raises a SessionError if session with same name already exists
		#creates an entry in the sessions table with start time now, and duration in days 
		#(change to configurable start time?)
		#creates a new table titled by the session phrase.
		#5 columns: lID, nodeID, time, lat, lon
		
		#make sure input is a number, ValueError raised otherwise
		days = float(days)
		
		#check if session exists
		if self.SessionExists(phrase):
			raise SessionError(phrase, SessionError.AE)
		else:
			#get the duration in days and make a time-delta object
			duration = datetime.timedelta(days=days)
			#set the current time as start
			now = datetime.datetime.now()
			start = now.strftime('%Y-%m-%d %H:%M:%S')
			#get the end time by adding days to current time
			endtime = now + duration
			end = endtime.strftime('%Y-%m-%d %H:%M:%S')			
			
			#insert into sessions table with no table name
			query = "INSERT INTO sessions (phrase, tblName, start, end) VALUES (%s, NULL, %s, %s)"
			self.cur.execute(query, (phrase, start, end))
			self.cur.connection.commit()
			#get the session ID of the new session row
			sID = self.cur.lastrowid
			
			#set a table name: simply 'session{sID}'
			tblName = 'session' + str(sID)
			
			#update the row to add tblName
			query = "UPDATE sessions SET tblName=%s WHERE phrase=%s"
			self.cur.execute(query, (tblName, phrase))
			
			#create table
			cols = "(lID INT NOT NULL AUTO_INCREMENT, nodeID INT NOT NULL, time DATETIME, lat FLOAT, lon FLOAT, PRIMARY KEY(lID))"
			query = "CREATE TABLE IF NOT EXISTS %s " + cols
			self.cur.execute(query % tblName)
			self.cur.connection.commit()			
			return
	
	def deleteSession(self, phrase):
		#deletes the session associated with the phrase
		#o.w. raises a Session DNE error
		session = self.getSession(phrase)
		tblName = str(session['tblName'])
		#delete the row from the session table
		self.cur.execute("DELETE FROM sessions WHERE phrase=%s", phrase)
		#drop the session table
		self.cur.execute("DROP TABLE " + tblName)
		#free all nodes in the session
		self.cur.execute("UPDATE nodes SET session=NULL WHERE session=%s", tblName) 
		self.cur.connection.commit()
	
	def SessionExists(self, phrase):
		#checks if a session exists, boolean function
		#returns true if session exists and false if it does not
		sessionExists = self.cur.execute("SELECT sID FROM sessions WHERE phrase=%s", phrase)
		return sessionExists
	
	def getSession(self, phrase):
		#gets a session from the sessions table and returns the whole row
		#raises a SessionError if the session does not exist
		sessionExists = self.cur.execute("SELECT * FROM sessions WHERE phrase=%s", phrase)
		if sessionExists == 0:
			raise SessionError(devID, SessionError.DNE)
		else:
			return self.cur.fetchone()
	
	def getSessions(self):
		#displays a list of all active sessions
		self.cur.execute("SELECT * FROM sessions")
		sessions = self.cur.fetchall()
		return sessions		
		
	"""NODE FUNCTIONS"""	
	def createNode(self, devID):
		#raises a NodeError.AE if node exists
		#o.w. creates a new node in the "nodes" table
		#the session it belongs to is defaulted to NULL
		#returns the nID if the node was created 	
		
		#check if the node already exists
		if self.NodeExists(devID):
			raise NodeError(devID, NodeError.AE)
		else:
			query = "INSERT INTO nodes (devID, session) VALUES (%s, NULL)"
			self.cur.execute(query, devID)	
			self.cur.connection.commit()
			#get the node ID
			nID = self.cur.lastrowid
			return nID
	
	def deleteNode(self, devID):
		#Removes the given node from the table of nodes
		#if the node is active, removes all the rows associated with the node in its session table	
		
		#check if node exists, raises NodeError if it does not exist
		node = self.getNode(devID)
		nID = node['nID']
		sessionTblName = node['session']
		#check if node is active
		if sessionTblName != None:
			#delete all rows in its session table associated with its nID
			self.cur.execute("DELETE FROM " + str(sessionTblName) + " WHERE nodeID=%s", nID) 
		#now delete it from the nodes table
		self.cur.execute("DELETE FROM nodes WHERE devID=%s", devID)
		self.cur.connection.commit()
	
	def activateNode(self, devID, phrase):
		#changes the session of a node to the new session iff the node exists AND is a free node
		
		#if the node does not exist or it is already in a session, raises a NodeError
		self.assertFreeNode(self.getNode(devID))
		
		#try to get the tblName of the session
		#SessionError.DNE raised if it fails
		session = self.getSession(phrase)
		tblName = session['tblName']
		
		#if all is well(no errors raised) update the row
		#set session table column to tblName
		query = "UPDATE nodes SET session=%s WHERE devID=%s"
		count = self.cur.execute(query, (tblName, devID))
		self.cur.connection.commit()
		return
			
	def freeNode(self, devID):
		#changes the session table column of a node to NULL
		query = "UPDATE nodes SET session=NULL WHERE devID=%s"
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
		nodeExists = self.cur.execute("SELECT * FROM nodes WHERE devID=%s", devID)
		if nodeExists == 0:
			raise NodeError(devID, NodeError.DNE)
		else:
			return self.cur.fetchone()
	
	def getNodes(self, phrase=0):
		#get all nodes
		if phrase == 0:
			self.cur.execute("SELECT * FROM nodes")
		else:
			#get the table name
			session = self.getSession(phrase)
			sessionTblName = session['session']
			self.cur.execute("SELECT * FROM nodes WHERE session=%s", sessionTblName)
		nodes = self.cur.fetchall()
		return nodes
	
	def NodeExists(self, devID):
		#checks if a node exists, boolean function
		#returns true if node exists and false if it does not
		nodeExists = self.cur.execute("SELECT nID FROM nodes WHERE devID=%s", devID)
		return nodeExists
	
	def assertFreeNode(self, node):
		#if node is not free raise NodeError
		if node['session'] != None:
			raise NodeError(node['devID'], NodeError.ACT)
		else:
			return node
			
	def assertActiveNode(self, node):
		#if node is free raise NodeError	
		if node['session'] == None:
			raise NodeError(node['devID'], NodeError.FRE)
		else:
			return node
			
	def checkNodeState(self, node):
		#checks why
		#if node is not free raise Active NodeError
		if node['session'] != None:
			raise NodeError(node['devID'], NodeError.ACT)
		#if the node is free raise Free NodeError
		else:
			raise NodeError(node['devID'], NodeError.FRE)
	
	"""LOCATION FUNCTIONS"""	
	def getLocations(self, tblName, nID):
		query = "SELECT * FROM {0} WHERE nID=%s".format(tblName)
		self.cur.execute(query, nID)
		return self.cur.fetchall()
	
	def createLocation(self, tblName, nID, time, lat, lon):
		query = "INSERT INTO {0} VALUES (NULL, %s, %s, %s, %s)".format(tblName)
		self.cur.execute(query, (nID, time, lat, lon))
		self.cur.connection.commit()
		lID = self.cur.lastrowid
		return lID
	
	def updateNodeLocation(self, nID, time, lat, lon):
		query = "UPDATE nodes SET time=%s, lat=%s, lon=%s WHERE nID=%s"
		self.cur.execute(query, (time, lat, lon, nID))
		self.cur.connection.commit()
		lID = self.cur.lastrowid
		return lID
		
	def deleteLocByLID(self, tblName, lID):
		query = "DELETE FROM {0} WHERE lID=%s".format(tblName)
		self.cur.executemany(query, lID)
		self.cur.connection.commit()

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
		
