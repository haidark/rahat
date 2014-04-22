##########################################################################
##########################################################################
##################### HARAMAIN FUNCTIONS #################################
##########################################################################
##########################################################################
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
def findNID_SessionbyDevID(cur, devID):
	query = "SELECT nID, session FROM nodes WHERE devID=%s"
	count = cur.execute(query, devID)
	if count == 1:
		first = cur.fetchall()[0]
		nID = first[0]
		session = first[1]
	else:
		print "Unique node not found for this device ID!!!!!"
		nID = -1
		session = -1
	return (nID, session)
	
def insertNodeInSession(cur, devID, session):
	query = "INSERT INTO nodes VALUES (NULL, %s, %s)"
	cur.execute(query, (devID, session))	
	#just in case
	cur.connection.commit()
	nID = cur.lastrowid
	if nID == None:
		print "Unable to insert new node!!!"
		nID = -1
	return nID
	
def insertLocationInSession(cur, session, nID, time, lat, lon):
	query = "INSERT INTO %s VALUES (NULL, %s, %s, %s, %s)"
	print query % (session, nID, time, lat, lon)
	cur.execute(query, (session, nID, time, lat, lon))
	#just in case
	cur.connection.commit()
	lID = cur.lastrowid
	if lID == None:
		print "Unable to insert new location!!!"
		lID = -1
	return lID