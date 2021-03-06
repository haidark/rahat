from threading import Thread
from DBManager import DBManager
from datetime import datetime, timedelta
from math import sqrt
from time import sleep
import logging

class NodeHandler(Thread):
	"""NodeHandler Class - inherits from threading.Thread
		Static Members:
			None
		Members:
			nID - node ID in nodes table
			devID - device ID for node
			tblName - name of the table of the session this node belongs to
			lastTime - last report time of this node
			lastLat, lastLon - last location of this node
			keepRunning - boolean used to tell the housekeeping thread to keep running or stop
			logger - handle for NodeHandler logger
		Functions:
			__init__(nodeData)
			update - updates object data to match with database
			setLocals(nodeData) - sets local members using a row from nodes table
			updateLocations() - gets all of this node's location data from its session table
			run() - runs housekeeping functions
			validateLocations() - makes sure location and time of every location row is valid
			compressLocations() - compresses location data by removing unneeded rows (stationary)
			validTime(locTime) - boolean function that checks if locTime is valid
			validLoc(locLat, locLon) - boolean function that checks if locLat and locLon are valid
			sameLoc(location1, location2) - takes 2 dicts with keys 'lat' and 'lon' and checks if
				they point to the same location (configurable tolerance value)
			returned() - boolean function to check if this node has been returned 
				TODO add return location to nodes table
			lastReportTime - returns a timedelta object representing time since last location report
	"""

	def __init__(self, nodeData):
		Thread.__init__(self)
		self.setLocals(nodeData)				
		self.updateLocations()
		self.keepRunning = True
		self.logger = logging.getLogger("node")
	
	def update(self):
		db = DBManager()
		nodeData = db.getNode(self.devID)		
		db.close()
		self.setLocals(nodeData)
	
	def setLocals(self, nodeData):
		self.nID = nodeData['nID']
		self.devID = nodeData['devID']
		self.sessionTblName = nodeData['session']
		self.lastTime = nodeData['time']
		self.lastLat = nodeData['lat']
		self.lastLon = nodeData['lon']
		self.contactID = nodeData['contactID']
		#if this node has been freed, stop the housekeeping threads
		if self.sessionTblName is None:
			self.keepRunning = False
		
	def updateLocations(self):
		db = DBManager()
		#get this nodes location data
		self.locations = db.getLocations(self.sessionTblName, self.nID)
		db.close()
		#if this node has no locations or is not in a sessions, stop the housekeeping threads
		if self.locations is None:
			self.keepRunning = False

	def run(self):
		self.logger.info("(+) NodeHandler for node:" +self.devID+" running")
		while self.keepRunning:			
			self.validateLocations()
			self.compressLocations()
			#delay for a bit to ease the load on the DB?
			sleep(30*60)
		self.logger.info("(+) NodeHandler for node:" +self.devID+" stopped")
		
	def validateLocations(self):
		#get updated location data from this nodes session table
		self.updateLocations()
		#initialize list to hold lID's of location rows to delete 
		locToDel = list()
		#loop over every location
		for location in self.locations:
			lID = location['lID']
			locTime = location['time']
			locLat = location['lat']
			locLon = location['lon']			
			# if the timestamp is invalid (in the future)
			if not self.validTime(locTime):
				locToDel.append(lID)
			# o.w. if the location is invalid
			elif not self.validLoc(locLat, locLon):
				locToDel.append(lID)
		#if there are locations to delete
		if locToDel:			
			#open a connection to the DB
			db = DBManager()		
			#delete the locations that were marked
			db.deleteLocByLID(self.sessionTblName, locToDel)
			#close the database connection
			db.close()
		
	def compressLocations(self):
		#get updated location data from this nodes session table
		self.updateLocations()		
		#initialize list to hold location rows to delete lID's
		#initialize Start and End
		locToDel = list()
		Start = 0
		End = 0
		
		#loop over every location
		for index, location in enumerate(self.locations):
			#skip the first iteration
			if index == 0:
				continue
			lID = location['lID']	
			#if location is the same at self.locations[Start]
			if self.sameLoc(location, self.locations[Start]):
				locToDel.append(lID)
				End = index
			else:
				if not Start == End:
					locToDel.pop()
				Start = index
				End = index
		
		#if there are locations to delete
		if locToDel:			
			#open a connection to the DB
			db = DBManager()		
			#delete the locations that were marked
			db.deleteLocByLID(self.sessionTblName, locToDel)
			#close the database connection
			db.close()
	
	#checks if the location time stamp is valid 	
	def validTime(self, locTime):
		now = datetime.now()
		return locTime < now
	
	#TODO checks if a location's coordinates are valid
	def validLoc(self, locLat, locLon):
		return True
	
	#checks if two locations are pointing to roughly the same area
	#location1 and location2 are dictionaries with keys 'lat' and 'lon'
	def sameLoc(self, location1, location2):
		tol = .00001
		lat1 = location1['lat']
		lon1 = location1['lon']
		lat2 = location2['lat']
		lon2 = location2['lon']
		#if no unavailable locations
		if not None in (lat1, lon1, lat2, lon2):
			lat1 = float(lat1)
			lon1 = float(lon1)
			lat2 = float(lat2)
			lon2 = float(lon2)
			#if euclidean distance is near 0
			d = sqrt((lat1-lat2)**2 + (lon1-lon2)**2)
			return d < tol
		else:
			#gracefully return False
			return False
	
	#boolean function to check if this node has been returned
	def returned(self):
		self.update()
		#put last locations in a dict object
		lastLoc = {'lat': self.lastLat, 'lon': self.lastLon}
		#TODO get return location from the nodes table
		returnLoc = {'lat': self.lastLat, 'lon': self.lastLon}
		return self.sameLoc(lastLoc, returnLoc)	

	#returns a timedelta object containing the difference in time
	#between now and the time last location was captured
	def lastReportTime(self):	
		self.update()
		now = datetime.now()
		#if no last report time
		if self.lastTime == None:
			return timedelta(minutes=100)
		else:
			return now - self.lastTime