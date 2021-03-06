from multiprocessing import Process
from DBManager import DBManager
from NodeHandler import NodeHandler
from datetime import datetime, timedelta
from time import sleep
import logging

class SessionHandler(Process):
	"""SessionHandler Class - inherits from multiprocessing.Process
		Static Members:
			None
		Members:
			sID - session ID in sessions table
			phrase - passphrase for session
			tblName - name of the table holding this sessions location data
			startTime - datetime object detailing when session started
			endTime - datetime object detailing when session will end
			nodes - list containing NodeHandler object for each node in session
			nodesDict - dict with devIDs of nodes as keys and ...
				value True if housekeeping thread has been started
				value False if housekeeping thread has not been started
			logger - handle for SessionHandler logger
			queue - Queue to place Alert objects on to send to Reporters
		Functions:
			__init__(sessionData)
			run() - runs main session loop until session expires, then terminates all child threads safely,
				archives session data and deletes session from database table
			update() - updates object data to match with session table row
			setLocals(sessionData) - takes a dict corresponding to a session table row 
				and sets local members
			createNodes() - gets rows from nodes table associated with this session and creates NodeHandler
				objects, also maintains a list of which objects have started their housekeeping threads. 
				is called multiple times without duplicating NodeHandler objects
			SessionActive() - boolean function to check if the session is active or not
			NodesHealthAlert() - Creates alerts if nodes are not healthy
	"""
	
	def __init__(self, sessionData, queue):
		Process.__init__(self)
		#initialize local members from passed DB data
		self.setLocals(sessionData)
		#initialize list to hold NodeHandler objects
		self.nodes = list()
		#initialize dictionary to hold state of housekeeping thread for each NodeHandler object
		#also prevents more than one NodeHandler to be instantiated for one node
		self.nodesDict = dict()
		#instantiate a NodeHandler object for each node in the session handled
		self.createNodes()
		self.logger = logging.getLogger("session")
		self.queue = queue
	
	def run(self):	
		#Main SessionHandler loop (runs while session is active)
		while self.SessionActive():
			#update local members from session table row
			self.update()
			#instantiate a NodeHandler object for each node in the session handled
			#subsequent calls will not create duplicates
			self.createNodes()
			#start the NodeHandler housekeeping threads
			#but first check if they have already been started
			for node in self.nodes:
				#if not started
				if not self.nodesDict[node.devID] :
					#start the thread
					node.start()
					#ensure start is not called again
					self.nodesDict[node.devID] = True

			self.NodesHealthAlert()
			#TODO write a function to relate nodes and check relations
			#how often do we want to repeat this? do not want to put too much strain on the DB
			#should check report times every minute or so
			sleep(2*60)
		
		# # # # # # After Session Expires # # # # # # 
		
		#---signal to stop to all housekeeping threads
		#tell the threads to stop
		for node in self.nodes:			
			self.logger.info(self.phrase+": signalling node:"+node.devID+" to stop running")
			node.keepRunning = False
		#wait for the threads to finish their work
		for node in self.nodes:				
			if node.is_alive():
				node.join()
				self.logger.info(self.phrase+": node:"+node.devID+" thread stopped")
		
		#---check if all nodes have been returned		
		# initialize list of unreturned nodes: using list comprehension
		unreturnedNodes = [node for node in self.nodes if not node.returned()]	
		# fire off an alert for every node that has not been returned
		for unreturnedNode in unreturnedNodes:
			#fire off an alerts to let session leader and node holder know this node has not been returned
			title = "Unreturned Node"
			message =  unreturnedNode.devID+" has not been returned."
			#create an alert for the session leader
			sessionAlert = Alert(self.contactID, message, title)
			self.queue.put(sessionAlert)
			#create an alert for the unreturned node holder
			nodeAlert = Alert(unreturnedNode.contactID, message, title)
			self.queue.put(nodeAlert)
		
		# now loop until all nodes are returned
		while unreturnedNodes:
			#check if any nodes have been returned
			unreturnedNodes = [node for node in unreturnedNodes if not node.returned()]
			#delay before checking again?
			sleep(5*60)

		# after all nodes are returned, archive the session table and delete its row from the database
		db = DBManager()
		db.deleteSession(self.phrase)
		db.close()
		#end the process
	
	def update(self):
		db = DBManager()
		sessionData = db.getSession(self.phrase)
		db.close()
		self.setLocals(sessionData)		
	
	def setLocals(self, sessionData):
		self.sID = sessionData['sID']
		self.phrase = sessionData['phrase']
		self.tblName = sessionData['tblName']
		self.startTime = sessionData['start']
		self.endTime = sessionData['end']
		self.contactID = sessionData['contactID']
	
	def createNodes(self):
		#get data for nodes in the session
		db = DBManager()		
		nodesData = db.getNodes(self.tblName)
		db.close()
		#create a new Node object for each nodeData row in nodesData 
		# if such an object does not already exist		
		for nodeData in nodesData:
			if not nodeData['devID'] in self.nodesDict:
				#add NodeHandler object to the list of nodes
				self.nodes.append(NodeHandler(nodeData))
				#add devID key to nodesDict and set to false(not started yet)
				self.nodesDict[nodeData['devID']] = False
				
	#boolean function to check if the session is active or not
	def SessionActive(self):
		#update values first
		self.update()
		#get current time
		now = datetime.now()
		# return true if expiration time has not been exceeded
		return self.endTime > now

	
	def NodesHealthAlert(self):
		#for each NodeHandler object
		for node in self.nodes:			
			#get timedelta object representing time since last location report
			timeSinceLast = node.lastReportTime()
			normalDiff = timedelta(minutes=5)
			warnDiff = timedelta(minutes=10)
			lostDiff = timedelta(minutes=15)
			if timeSinceLast < normalDiff:
				#node is healthy, nothing to do here
				pass
			elif timeSinceLast < warnDiff:
				#warning about time since last report
				title = "Report Time Warning"
				message = "Node: "+str(node.devID)+" has not reported for "+str(timeSinceLast.seconds/60)+" minutes"
				#create alert for session leader
				sessionAlert = Alert(self.contactID, message, title)
				self.queue.put(sessionAlert)
			elif timeSinceLast > lostDiff:
				#the node is lost
				pass
			else:
				#The node has not reported in a long time
				title = "Report Time Alert"
				message = "Node: "+str(node.devID)+" has not reported for "+str(timeSinceLast.seconds/60)+" minutes"
				#create alert for session leader
				sessionAlert = Alert(self.contactID, message, title)
				self.queue.put(sessionAlert)

class Alert:
	"""Alert class packages data that needs to be sent to the Reporters from the SessionHandlers
		Static Members:
			None
		Members:
			contactID
			message
			title
		Functions:
			__init__(contactID, message, [title])
	"""
	def __init__(self, contactID, message, title="Rahat Alert Message"):
		self.contactID = contactID
		self.message = message
		self.title = title
				