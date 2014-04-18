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
	query = "INSERT INTO locations VALUES (NULL, %d, %s, %s, %s)"
	cur.execute(query, (NID, time, lat, lon))
	#just in case
	cur.connection.commit()
	LID = cur.lastrowid
	if LID == None:
		print "Unable to insert new node!!!"
		LID = -1
	return LID