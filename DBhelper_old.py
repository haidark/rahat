##########################################################################
##########################################################################
##################### HARAMAIN FUNCTIONS #################################
##########################################################################
##########################################################################
def findSIDbyPhrase(cur, phrase):	
	query = "SELECT SID FROM sessions WHERE phrase=%s"
	count = cur.execute(query, phrase)
	if count == 1:
		SID = cur.fetchone()[0]
	else:
		print "Unique session not found for this phrase!!!!!"
		SID = -1	
	return SID
	
def findNIDbyInfo(cur, info):
	query = "SELECT NID FROM nodes WHERE info=%s"
	count = cur.execute(query, info)
	if count == 1:
		NID = cur.fetchone()[0]
	else:
		print "Unique node not found for this info!!!!!"
		NID = -1
	return NID

def insertNode(cur, SID, info):
	query = "INSERT INTO nodes VALUES (NULL, %s, %s)"
	cur.execute(query, (SID, info))
	#just in case
	cur.connection.commit()
	NID = cur.lastrowid
	if NID == None:
		print "Unable to insert new node!!!"
		NID = -1
	return NID
	
def insertLocation(cur, NID, time, lat, lon):
	query = "INSERT INTO locations VALUES (NULL, %s, %s, %s, %s)"
	cur.execute(query, (NID, time, lat, lon))
	#just in case
	cur.connection.commit()
	LID = cur.lastrowid
	if LID == None:
		print "Unable to insert new location!!!"
		LID = -1
	return LID


##########################################################################
##########################################################################
##################### HARAMAIN 2 FUNCTIONS ###############################
##########################################################################
##########################################################################
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
		
def createNode(cur, devID, session='NULL'):
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
		if ne.msg == NodeError.DNE
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
	
def addNodetoSession(cur, devID, session):
	#changes the session of a node to the new session iff the node exists AND is a free node
	
	#if the node does not exist or it is already in a session, raises a NodeError
	assertFreeNode(getNode(cur, devID))
	#if all is well(no errors raised)
	query = "UPDATE nodes SET session=%s WHERE devID=%s AND session=NULL"
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

def SessionExists(cur, session):
	#checks if a session exists, boolean function
	#returns 1 if session exists and 0 if it does not
	return cur.execute("SHOW TABLES LIKE %s", session);
		
def insertLocationInSession(cur, session, nID, time, lat, lon):
	if !SessionExists(cur, session):
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
		
	
##########################################################################
##########################################################################
##################### Exception definitions ##############################
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
		
	Types:"""
	DNE = "Node Does Not Exist"
	AE = "Node Already Exists"
	ACT = "Node is Active"
	FRE = "Node is Free"
    def __init__(self, devID, msg):
        self.devID = devID
        self.msg = msg

class SessionError(Error):
    """Exception raised for errors related to sessions.

    Attributes:
        session -- input session for which session error occurred
        msg  -- explanation of the error
		
	Types:"""
	DNE = "Session Does Not Exist"
	AE = "Session Already Exists"
	
    def __init__(self, session, msg):
        self.session = session
        self.msg = msg
		
class FieldError(Error):
    """Exception raised for errors related to invalid fields.

    Attributes:
        field -- input field for which field error occurred
        msg  -- explanation of the error
		
	Types:"""
	IP = "Invalid Phrase for Session"
	ID = "Invalid devID for Node"
    def __init__(self, field, msg):
        self.field = field
        self.msg = msg