import socket
from Listener import Listener
from Reporter import Reporter
from DBManager import DBManager
from SessionHandler import SessionHandler
from multiprocessing import Queue
from time import sleep
import logging, logging.handlers

#########Create/Configure Loggers for each module#######################
#format of log messages
formatter = logging.Formatter("%(asctime)s: %(message)s")
#Overseer.log
overseerlogger = logging.getLogger("overseer")
overseerlogger.setLevel(logging.DEBUG)
overseerfh = logging.handlers.RotatingFileHandler('logs/Overseer.log', maxBytes = 10*1024*1024, backupCount=2)
overseerfh.setFormatter(formatter)
overseerlogger.addHandler(overseerfh)

#SessionHandler.log
sessionlogger = logging.getLogger("session")
sessionlogger.setLevel(logging.DEBUG)
sessionfh = logging.handlers.RotatingFileHandler('logs/SessionHandler.log', maxBytes = 10*1024*1024, backupCount=2)
sessionfh.setFormatter(formatter)
sessionlogger.addHandler(sessionfh)

#NodeHandler.log
nodelogger = logging.getLogger("node")
nodelogger.setLevel(logging.DEBUG)
nodefh = logging.handlers.RotatingFileHandler('logs/NodeHandler.log', maxBytes = 10*1024*1024, backupCount=2)
nodefh.setFormatter(formatter)
nodelogger.addHandler(nodefh)

#Listener.log
listenerlogger = logging.getLogger("listener")
listenerlogger.setLevel(logging.DEBUG)
listenerfh = logging.handlers.RotatingFileHandler('logs/Listener.log', maxBytes = 10*1024*1024, backupCount=2)
listenerfh.setFormatter(formatter)
listenerlogger.addHandler(listenerfh)

#Reporter.log
reporterlogger = logging.getLogger("reporter")
reporterlogger.setLevel(logging.DEBUG)
reporterfh = logging.handlers.RotatingFileHandler('logs/Reporter.log', maxBytes = 10*1024*1024, backupCount=2)
reporterfh.setFormatter(formatter)
reporterlogger.addHandler(reporterfh)

########initialize Listeners
#first create server socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('192.168.1.222', 1060))
overseerlogger.info("(+) Listening socket created.")
#create 5 Listeners and start them
for i in range(5):
	t = Listener(sock, i+1)
	t.start()
	overseerlogger.info("(+) Listener "+str(i+1)+" started.")

########Initialize Alert Queue
alertQueue = Queue()

########initialize Reporter
reporter = Reporter(alertQueue, 0)
reporter.start()
overseerlogger.info("(+) Reporter started.")
	
########Initialize dict to hold phrases of active sessions and their states
sessionsDict = dict()
#Initialize list to hold SessionHanlder objects
sessionHandlers = list()

########Manage session loop
while True:
	#connect to the database
	db = DBManager()
	#get all sessions data from DB
	sessions = db.getSessions()
	db.close()
	#overseerlogger.info("(+) Retrieved Session information from DB")
	#generate SessionHandler objects add keys to sessionDict
	#for each row in sessions table
	for session in sessions:
		#if this row does not have a sessionHandler, make one for it and start it
		if not session['phrase'] in sessionsDict:
			sessionHandler = SessionHandler(session, alertQueue)
			sessionHandlers.append(sessionHandler)
			sessionHandler.start()
			overseerlogger.info("(+) SessionHandler for session:"+sessionHandler.phrase+" started.")
			sessionsDict[session['phrase']] = True
			
	#cleanup SessionHandler objects and remove keys from sessionsDict
	#Dict to hold all phrases of active sessions (from database) (dict is faster than list)
	phraseDict = {session['phrase']:1 for session in sessions}
	
	#remove sessionHandlers that have ended and sessions that have expired (phrase not in phraseList)
	for sessionHandler in sessionHandlers[:]:
		if not sessionHandler.is_alive():
			del sessionsDict[sessionHandler.phrase]
			sessionHandlers.remove(sessionHandler)
			overseerlogger.info("(+) SessionHandler for session:"+sessionHandler.phrase+" destroyed.")
		elif not sessionHandler.phrase in phraseDict: 	
			del sessionsDict[sessionHandler.phrase]
			sessionHandler.terminate()
			sessionHandlers.remove(sessionHandler)
			overseerlogger.info("(+) SessionHandler for session:"+sessionHandler.phrase+" terminated and destroyed.")
	#wait 30 minutes		
	sleep(30*60)
	