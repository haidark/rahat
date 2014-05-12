import socket
from Listener import Listener
from DBManager import DBManager
from SessionHandler import SessionHandler
from time import sleep

if __name__=="__main__":
	
	#initialize Listeners
		#first create server socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind(('192.168.1.222', 1060))
	print "(+) Listening socket created."
		#create 5 Listeners and start them
	for i in range(5):
		t = Listener(sock, i+1)
		t.start()
		print "(+) Listener "+str(i+1)+" started."
	
	#Initialize dict to hold phrases of active sessions and their states
	sessionsDict = dict()
	#Initialize list to hold SessionHanlder objects
	sessionHandlers = list()
	
	#Manage session loop
	while True:
		#connect to the database
		db = DBManager()
		#get all sessions data from DB
		sessions = db.getSessions()
		db.close()
		print "(+) Retrieved Session information from DB"
		#generate SessionHandler objects add keys to sessionDict
		#for each row in sessions table
		for session in sessions:
			print session
			#if this row does not have a sessionHandler, make one for it and start it
			if not session['phrase'] in sessionsDict:
				sessionHandler = SessionHandler(session)
				sessionHandlers.append(sessionHandler)
				sessionHandler.start()
				print "(+) SessionHandler for session:"+sessionHandler.phrase+" started."
				sessionsDict[session['phrase']] = True
				
		#cleanup SessionHandler objects and remove keys from sessionsDict
		#Dict to hold all phrases of active sessions (from database) (dict is faster than list)
		phraseDict = {session['phrase']:1 for session in sessions}
		
		#remove sessionHandlers that have ended and sessions that have expired (phrase not in phraseList)
		for sessionHandler in sessionHandlers[:]:
			if not sessionHandler.is_alive():
				del sessionsDict[sessionHandler.phrase]
				sessionHandlers.remove(sessionHandler)
				print "(+) SessionHandler for session:"+sessionHandler.phrase+" destroyed."
			elif not sessionHandler.phrase in phraseDict: 	
				del sessionsDict[sessionHandler.phrase]
				sessionHandler.terminate()
				sessionHandlers.remove(sessionHandler)
				print "(+) SessionHandler for session:"+sessionHandler.phrase+" terminated and destroyed."
		#wait 1 minute		
		sleep(60)
		print "(+) Waiting 1 minute."