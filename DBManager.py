import pymysql
import datetime
import re

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
			setSessionPeriod(phrase, days) - sets start and end columns of the session row keyed by phrase			
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
			
			----Contacts-------------------------------------------------------------------------------------------
			createContact([fName, lName, email, phone]) - creates a new contact
			deleteContact([fName, lName, email, phone]) - deletes a given contact
			findContact([cID, fName, lName, email, phone]) - finds the contact with given info			
			assignSession(phrase, [cID, fName, lName, email, phone]) - assigns the session to a contact in the contact table
			unassignSession(phrase) - unassigns the session from a contact
			assignNode(devID, [cID, fName, lName, email, phone]) - assigns the node to a contact
			unassignNode(devID) - unassigns the node from a contact
			getContacts() - gets all contacts in the contacts table
			contactExists(fName, lName, email, phone) - boolean function to check if a contact exists
			checkFields([fName, lName, email, phone]) - checks to make sure all fields are valid
			assertUnassigned(row) - asserts a session or node is unassigned
			assertAssigned(row) - asserts a session or not is assigned
			
			----Locations------------------------------------------------------------------------------------------
			getLocations(tblName, nID) - gets all locations of a node in a session table
			createLocation(tblName, nID, time, lat, lon) - adds location row to a session table
			updateNodeLocation(nID, time, lat, lon) - updates last known location of node
			deleteLocByLID(tblName, lID) - deletes location row or rows in a session table
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
	def createSession(self, phrase):		
		#raises a SessionError if session with same name already exists
		#creates a row in the sessions table
		#creates a new table titled by the session phrase.
		#5 columns: lID, nodeID, time, lat, lon		
		
		#check if session exists
		if self.SessionExists(phrase):
			raise SessionError(phrase, SessionError.AE)
		else:
			#insert into sessions table with no table name
			query = "INSERT INTO sessions (phrase, tblName) VALUES (%s, NULL)"
			self.cur.execute(query, phrase)
			self.cur.connection.commit()
			#get the session ID of the new session row
			sID = self.cur.lastrowid
			
			#set a table name: simply 'session{sID}'
			tblName = 'session' + str(sID)
			
			#update the row to add tblName
			query = "UPDATE sessions SET tblName=%s WHERE sID=%s"
			self.cur.execute(query, (tblName, str(sID)))
			
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
	
	def setSessionPeriod(self, phrase, days):
		#sets duration of an entry in the sessions table with start time now, and duration in days 
		
		#make sure input is a number, ValueError raised otherwise
		days = float(days)
		#get the duration in days and make a time-delta object
		duration = datetime.timedelta(days=days)
		#set the current time as start
		now = datetime.datetime.now()
		start = now.strftime('%Y-%m-%d %H:%M:%S')
		#get the end time by adding days to current time
		endtime = now + duration
		end = endtime.strftime('%Y-%m-%d %H:%M:%S')	
		
		#get the session keyed by the phrase
		session = self.getSession(phrase)
		
		query = "UPDATE sessions SET start=%s, end=%s WHERE sID=%s"
		self.cur.execute(query, (start, end, session['sID']))
		self.cur.connection.commit()
		return		
		
	def getSession(self, phrase):
		#gets a session from the sessions table and returns the whole row
		#raises a SessionError if the session does not exist
		sessionExists = self.cur.execute("SELECT * FROM sessions WHERE phrase=%s", phrase)
		if sessionExists == 0:
			raise SessionError(phrase, SessionError.DNE)
		else:
			return self.cur.fetchone()
			
	def getSessions(self):
		#displays a list of all active sessions
		self.cur.execute("SELECT * FROM sessions")
		sessions = self.cur.fetchall()
		return sessions		
	
	def SessionExists(self, phrase):
		#checks if a session exists, boolean function
		#returns true if session exists and false if it does not
		sessionExists = self.cur.execute("SELECT sID FROM sessions WHERE phrase=%s", phrase)
		return sessionExists
		
	
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
			sessionTblName = session['tblName']
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
			
		
	"""CONTACT FUNCTIONS"""
	def createContact(self, fName=None, lName=None, email=None, phone=None):
		#first check if fields are valid
		self.checkFields(fName=fName, lName=lName, email=email, phone=phone)
		#create an entry in the contacts table if one does not already exist
		if not self.contactExists(fName=fName, lName=lName, email=email, phone=phone):
			query = "INSERT INTO contacts (fName, lName, email, phone) VALUES (%s, %s, %s, %s)"
			self.cur.execute(query, (fName, lName, email, phone))
			self.cur.connection.commit()
			#get the node ID
			cID = self.cur.lastrowid
			return cID
		else:
			raise ContactError(lName, ContactError.AE)
			
	def deleteContact(self, fName=0, lName=0, email=0, phone=0):
		contact = self.findContact(fName, lName, email, phone)		
		#drop the row from the contacts table
		query = "DELETE FROM contacts WHERE cID=%s"
		self.cur.execute(query, contact['cID'])
		#remove any reference to it from nodes table
		query = "UPDATE nodes SET contactID=NULL WHERE contactID=%s"
		self.cur.execute(query, contact['cID'])
		#remove any reference to it from sessions table
		query = "UPDATE sessions SET contactID=NULL WHERE contactID=%s"
		self.cur.execute(query, contact['cID'])
		self.cur.connection.commit()
		
	def findContact(self, cID=0, fName=0, lName=0, email=0, phone=0):			
		#check if no argument provided
		if fName is 0 and lName is 0 and email is 0 and phone is 0 and cID is 0:
			raise ContactError("Find", ContactError.FA)
		#first check if cID is provided, if it is, get the contact immediately
		if cID is not 0:
			query = "SELECT * FROM contacts WHERE cID=%s"
			contactExists = self.cur.execute(query, cID)
		#otherwise search for the contact using the other parameters
		else:		
			#assemble the proper where clause for these arguments
			#holds individual clauses
			clauses = []
			#holds value to check, is converted to tuple at the end
			values = []
			#include clauses for included arguments
			if fName is not 0:
				clauses.append("fName=%s")
				values.append(fName)
			if lName is not 0:
				clauses.append("lName=%s")
				values.append(lName)
			if email is not 0:
				clauses.append("email=%s")
				values.append(email)
			if phone is not 0:
				clauses.append("phone=%s")
				values.append(phone)
			#after clauses are put into array
			#check if just one clause is provided, if so pass it directly
			if len(clauses) is 1:
				whereClause = clauses[0]
			#otherwise, join the clauses with AND
			else:
				whereClause = ' AND '.join(clauses)

			#assemble final query
			query = "SELECT * FROM contacts WHERE " + whereClause
			contactExists = self.cur.execute(query, tuple(values))
		
		if contactExists == 1:
			return self.cur.fetchone()
		elif contactExists == 0:
			raise ContactError("Find", ContactError.DNE)
		elif contactExists > 1:
			raise ContactError("Find", ContactError.MTO)
			
	def assignSession(self, phrase, cID=0, fName=0, lName=0, email=0, phone=0):
		session = self.getSession(phrase)
		#raises error if session is already assigned to a person
		self.assertUnassigned(session)
		#get the contact info of the person
		contact = self.findContact(cID=cID, fName=fName, lName=lName, email=email, phone=phone)		
		query = "UPDATE sessions SET contactID=%s WHERE sID=%s"
		self.cur.execute(query, (contact['cID'], session['sID']))
		self.cur.connection.commit()
		return
		
	def unassignSession(self, phrase):
		session = self.getSession(phrase)
		#raises error if session is not assigned to a person
		self.assertAssigned(session)		
		query = "UPDATE sessions SET contactID=NULL WHERE sID=%s"
		self.cur.execute(query, session['sID'])
		self.cur.connection.commit()
		return
	
	def assignNode(self, devID, cID=0, fName=0, lName=0, email=0, phone=0):
		node = self.getNode(devID)
		#raises error if node is already assigned to a person
		self.assertUnassigned(node)
		#get the contact info of the person
		contact = self.findContact(cID=cID, fName=fName, lName=lName, email=email, phone=phone)		
		query = "UPDATE nodes SET contactID=%s WHERE nID=%s"
		self.cur.execute(query, (contact['cID'], node['nID']))
		self.cur.connection.commit()
		return
	
	def unassignNode(self, devID):
		node = self.getNode(devID)
		#raises error if node is not assigned to a person
		self.assertAssigned(node)		
		query = "UPDATE nodes SET contactID=NULL WHERE nID=%s"
		self.cur.execute(query, node['nID'])
		self.cur.connection.commit()
		return
	
	def getContacts(self):
		query = "SELECT * FROM contacts"
		self.cur.execute(query)
		return self.cur.fetchall()
	
	def contactExists(self, fName=None, lName=None, email=None, phone=None):
		#returns 0 if contact with given parameters does not exist
		#otherwise returns 1
		query = "SELECT cID FROM contacts where fName=%s AND lName=%s AND email=%s AND phone=%s"
		return self.cur.execute(query, (fName, lName, email, phone))
	
	def checkFields(self, fName=None, lName=None, email=None, phone=None):
		#raise errors if first name and last name are not all letters
		if fName is not None and not fName.isalpha():
			raise ContactError(fName, ContactError.IN)		
		if lName is not None and not lName.isalpha():
			raise ContactError(lName, ContactError.IN)
			
		#raise error if email is not in proper format
		if email is not None and not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
			raise ContactError(email, ContactError.IE)
			
		#raise error if phone is not all numbers
		if phone is not None and not phone.isdigit():
			raise ContactError(phone, ContactError.IP)
	
	def assertUnassigned(self, row):
		#if row is assigned raise ContactError
		if row['contactID'] != None:
			raise ContactError("Row", ContactError.AA)
		else: 
			return row
			
	def assertAssigned(self, row):
		#if row is unassigned raise ContactError
		if row['contactID'] == None:
			raise ContactError("Row", ContactError.NA)
		else: 
			return row
	
	
	"""LOCATION FUNCTIONS"""	
	def getLocations(self, tblName, nID):
		query = "SELECT * FROM {0} WHERE nodeID=%s".format(tblName)
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
	AA = "Session is already assigned"
	NA = "Session is not assigned"
	
class ContactError(Error):
	"""Exception raised for errors related to contacts.

	Attributes:
	contact -- input contact for which contact error occurred
	msg  -- explanation of the error
	"""	
	
	def __init__(self, contact, msg):
		self.contact = contact
		self.msg = msg
	
	#Error types
	DNE = "Contact Does Not Exist"
	AE = "Contact Already Exists"
	MTO = "More than one Contact matches"
	IN = "Invalid fName or lName"
	IE = "Invalid Email"
	IP = "Invalid Phone"
	AA = "Row is already assigned"
	NA = "Row is not assigned"
	FA = "Too few arguments provided"
