from errors import SessionError, NodeError, FieldError

##########################################################################
##########################################################################
##################### HARAMAIN 2 FUNCTIONS ###############################
##########################################################################
##########################################################################

"""SESSION FUNCTIONS"""
def createSession(cur, session):
	#creates a new table titled by the session phrase.
	#raises a SessionError if table with same name already exists
	#5 columns: lID, nodeID, time, lat, lon
	if SessionExists(cur, session):
		raise SessionError(session, SessionError.AE)
	else:
		cols = "(lID INT NOT NULL AUTO_INCREMENT, nodeID INT NOT NULL, time DATETIME, lat FLOAT, lon FLOAT, PRIMARY KEY(lID))"
		query = "CREATE TABLE IF NOT EXISTS %s " + cols
		cur.execute(query % session)
		cur.connection.commit()
		return

def deleteSession(cur, session):
	#drops the table associated with a session
	if ~SessionExists(cur, session):
		raise SessionError(session, SessionError.DNE)
	else:
		cur.execute("DROP TABLE " + str(session))
	
def SessionExists(cur, session):
	#checks if a session exists, boolean function
	#returns 1 if session exists and 0 if it does not
	return cur.execute("SHOW TABLES LIKE %s", session)

"""NODE FUNCTIONS"""	
def createNode(cur, devID, session=None):
	#creates a new node in the "nodes" table
	#the session it belongs to is optional and defaulted to NULL
	#returns the nID if the node was created or found in the table
	
	#check if the node already exists
	try:
		node = getNode(cur, devID)
		print "Node with devID=%s already exists." % devID
		return node[0]
	#if the node does not exist
	except NodeError as ne:		
		if ne.msg == NodeError.DNE:
			query = "INSERT INTO nodes VALUES (NULL, %s, %s)"
			cur.execute(query, (devID, session))	
			cur.connection.commit()
			#get the node ID
			nID = cur.lastrowid
			#Never expect this if statement to pass but leaving it in there just in case
			if nID == None:
				print "Unable to create new node."
				nID = -1
			return nID

def deleteNode(cur, devID):
	#Removes the given node from the table of nodes
	#if the node is active, removes all the rows associated with the node in its session table	
	
	#check if node exists, raises NodeError if it does not exist
	node = getNode(cur, devID)
	nID = node[0]
	session = node[2]
	#check if node is active
	if session != 'NULL':
		#delete all rows in its session table associated with its nID
		cur.execute("DELETE FROM " + str(session) + " WHERE nodeID=%s", nID) 
	#now delete it from the nodes table
	cur.execute("DELETE FROM nodes WHERE devID=%s", devID)
			
def activateNode(cur, devID, session):
	#changes the session of a node to the new session iff the node exists AND is a free node
	
	#if the node does not exist or it is already in a session, raises a NodeError
	assertFreeNode(getNode(cur, devID))
	#if all is well(no errors raised)
	query = "UPDATE nodes SET session=%s WHERE devID=%s"
	count = cur.execute(query, (session, devID))
	cur.connection.commit()
	return
		
def freeNode(cur, devID):
	#changes the session column of a node to NULL
	query = "UPDATE nodes set session=NULL WHERE devID=%s"
	count = cur.execute(query, devID)
	#if something goes wrong
	if count == 0:
		#check if node exists or node was already free
		checkNodeState(getNode(cur, devID))
	else:
		return

def getNode(cur, devID):
	#gets a node from the nodes table and returns the whole row
	#raises a NodeError if the node does not exist
	nodeExists = cur.execute("Select * from nodes WHERE devID=%s", devID)
	if nodeExists == 0:
		raise NodeError(devID, NodeError.DNE)
	else:
		return cur.fetchone()
		
def assertFreeNode(node):
	#if node is not free raise NodeError
	if node[2] != 'NULL':
		raise NodeError(devID, NodeError.ACT)
	else:
		return node

def assertActiveNode(node):
	#if node is free raise NodeError	
	if node[2] == 'NULL':
		raise NodeError(devID, NodeError.FRE)
	else:
		return node

def checkNodeState(node):
	#checks why
	#if node is not free raise Active NodeError
	if node[2] != 'NULL':
		raise NodeError(devID, NodeError.ACT)
	#if the node is free raise Free NodeError
	else:
		raise NodeError(devID, NodeError.FRE)
		
"""LOCATION FUNCTIONS"""	
def createLocation(cur, session, nID, time, lat, lon):
	if ~SessionExists(cur, session):
		raise SessionError(session, SessionError.DNE)
	else:
		query = "INSERT INTO {0} VALUES (NULL, %s, %s, %s, %s)".format(session)
		cur.execute(query, (nID, time, lat, lon))
		cur.connection.commit()
		lID = cur.lastrowid
		#Never expect this if statement to pass but leaving it in there just in case
		if lID == None:
			print "Unable to insert new location!!!"
			lID = -1
		return lID	
		
"""DISPLAY FUNCTIONS"""

def displaySessions(cur):
	#displays a list of all active sessions
	pass
	
def displayNodes(cur, session=0):
	#displays a list of all nodes
	if session == 0:
		cur.execute("SELECT * FROM nodes")
	else:
		cur.execute("SELECT * FROM nodes WHERE session=%s", session)
	nodes = cur.fetchall()
	for node in nodes:
		print node

		
