#!/usr/bin/env python

from DBManager import DBManager, SessionError, NodeError

import argparse
parser = argparse.ArgumentParser()

#-s SESSIONNAME to create a new session
parser.add_argument("-s", "--session", help="create a new session", metavar='passphrase')
#-a SESSIONNAME to archive a session
parser.add_argument("-a", "--archive", help="archive a session", metavar='passphrase')
#-n DEVID to create a new node
parser.add_argument("-n", "--node", help="create a new node", metavar='deviceID')
#-d DEVID to delete a node
parser.add_argument("-d", "--delete", help="delete a node", metavar='deviceID')
#-u DEVID SESSIONNAME to activate a node
parser.add_argument("-u", "--activate", help="add a node to a session", nargs=2, metavar=('deviceID', 'passphrase'))
#-f DEVID to free a node
parser.add_argument("-f", "--free", help="free a node", metavar='deviceID')
#-S to list all active sessions
parser.add_argument("-S", "--SESSIONS", help="list all active sessions", action="store_true")
#-N to list all nodes and include [SESSIONNAME] to list all nodes in a session
parser.add_argument("-N", "--NODES", help="list all nodes in a session, use 0 for a list of all nodes", metavar='passphrase')

args = parser.parse_args()

DBINFO = ('127.0.0.1', 'haidar', 'pin101', 'haramain2')
db = DBManager(DBINFO)

if args.session != None:
	#create a new session
	db.createSession(args.session)
	print "Created session with passphrase: " + args.session
	
elif args.archive != None:
	#archive session
	db.deleteSession(args.archive)
	print "Deleted session with passphrase: " + args.archive
	
elif args.node != None:
	#create a new node
	db.createNode(args.node)

	print "Created node with device ID: " + args.node
	
elif args.delete != None:
	#delete a node
	db.deleteNode(args.delete)
	print "Deleted node with device ID: " + args.delete
	
elif args.activate != None:
	#activate a node
	db.activateNode(args.activate[0], args.activate[1])
	print "Added node with device ID: " + args.activate[0] + " to session with passphrase: " + args.activate[1]
	
elif args.free != None:
	#free a node
	db.freeNode(args.free)
	print "Freed node with device ID: " + args.free
	
elif args.SESSIONS == True:
	#list all sessions
	print "\t-----Session List-----"
	db.displaySessions()
	
elif args.NODES != None:
	#list nodes
	if args.NODES == '0':
		print "\t-----Node List-----"
		db.displayNodes()
	else:
		print "\t-----Node List in Session : %s-----" % args.NODES
		db.displayNodes(args.NODES)
	
else:
#------------------------------------------TESTING CODE---------------------------------------------------#	
	ses = 'testsession'
	dev1 = 'testdevx'
	dev2 = 'testdevy'
	dev3 = 'testdevz'
	dev4 = 'testdevu'
#---------------------------------------------------------------------------------------------------------#	
#---------------------------------------------------------------------------------------------------------#	
	print "(========)Testing all DB managing functions(========)"
#---------------------------------------------------------------------------------------------------------#	
#---------------------------------------------------------------------------------------------------------#	
	print "(========)SESSION FUNCTION TESTS(========)"	
#---------------------------------------------------------------------------------------------------------#	
	print "(=) Creating a new session called '%s'" % ses
	try:
		db.createSession(ses)
	except SessionError as se:
		pass
	print "\t(+) Session created!"
#---------------------------------------------------------------------------------------------------------#	
	print "(=) Testing displaySessions function"
	print "(=) List of all sessions"
	db.displaySessions()
#---------------------------------------------------------------------------------------------------------#	
	print "(=) Testing Failure of createSession function"
	try:
		db.createSession(ses)
		print "\t(-) Failure of createSession Test Failed"
	except SessionError as se:
		print "\t(+) Failure of createSession Test Passed. Error Caught:", se.msg
#---------------------------------------------------------------------------------------------------------#		
#---------------------------------------------------------------------------------------------------------#		
	print "(========)NODE FUNCTION TESTS(========)"
#---------------------------------------------------------------------------------------------------------#		
	print "(=) Creating nodes"
	d1 = db.createNode(dev1, ses)
	d2 = db.createNode(dev2)
	d3 = db.createNode(dev3);	

	if d1 == -1 or d2 == -1 or d3 == -1:
		print "\t(-) Node Creation failed."
	else:
		print "\t(+) Nodes created."
#---------------------------------------------------------------------------------------------------------#	
	print "(=) Testing displayNodes function"
	print "(=) List of all nodes"
	db.displayNodes()
	print "(=) List of all nodes in session=%s" % ses
	db.displayNodes(ses)
#---------------------------------------------------------------------------------------------------------#		
	print "(=) Testing creation of existing node"
	dx = db.createNode(dev1, ses)
	if dx == d1:
		print "\t(+) Existing Node Creation Test Passed. nIDs are the same. Warning printed"
	else:
		print "\t(-) Existing Node Creation Test Failed. nIDs are not the same. Printing list of all Nodes."
		db.displayNodes()
#---------------------------------------------------------------------------------------------------------#	
	print "(=) Testing creation of node with invalid session"
	try:
		db.createNode(dev4, 'invalidsession')
		print "\t(-) Invalid Session Node Test failed."
	except SessionError as se:
		print "\t(+) Invalid Session Node Test passed. Error Caught: ", se.msg
#---------------------------------------------------------------------------------------------------------#		
	print "(=) activateNode Test"
	
	print "(=) activating device=%s" % dev2
	db.activateNode(dev2, ses)
	print "\t(+) Activated, printing all nodes in %s" % ses
	db.displayNodes(ses)
#---------------------------------------------------------------------------------------------------------#		
	print "(=) Assert Free Node Test"
	try:
		db.activateNode(dev2, ses)
		print "\t(-) Assert Free Node Test Failed"
	except NodeError as ne:
		print "\t(+) Assert Free Node Test Passed. Error Caught: ", ne.msg
#---------------------------------------------------------------------------------------------------------#			
	print "(=) freeNode Test"

	print "(=) freeing device=%s" % dev1
	db.freeNode(dev1)
	print "\t(+) Freed, printing all nodes"
	db.displayNodes()
#---------------------------------------------------------------------------------------------------------#		
	print "(=) Check Node State Test"
	try:
		db.freeNode(dev1)
		print "\t(-) Check Node State Test Failed"
	except NodeError as ne:
		print "\t(+) Check Node State Test Passed. Error Caught: ", ne.msg
#---------------------------------------------------------------------------------------------------------#		
	print "(=) deleteNode Test"
	
	print "(=) deleting device=%s" % dev3
	db.deleteNode(dev3)
	
	print "(=) deleting non-existent device."
	try:
		db.deleteNode('devu')
		print "\t(-) deleteNode Test Failed."
	except NodeError as ne:
		print "\t(+) deleteNode Test Passed. Error Caught: ", ne.msg
#---------------------------------------------------------------------------------------------------------#		
	print "(=) Cleaning up...."		
	db.deleteNode(dev1)
	db.deleteNode(dev2)	
	db.deleteSession(ses)		
	db.close()	
#---------------------------------------------------------------------------------------------------------#	