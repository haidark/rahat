#!/usr/bin/env python

from DBManager import DBManager, SessionError, NodeError

import argparse
parser = argparse.ArgumentParser()

#-s SESSIONNAME DAYS to create a new session for DAYS days
parser.add_argument("-s", "--session", help="create a new session for days", nargs=2, metavar=('passphrase', 'days'))
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

db = DBManager()

if args.session != None:
	#create a new session
	db.createSession(args.session[0], int(args.session[1]))
	print "Created session with passphrase: " + args.session[0] + " for " + args.session[1] + " days"
	
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
	sessions = db.getSessions()
	for session in sessions:
		print session
	
elif args.NODES != None:
	#list nodes
	if args.NODES == '0':
		print "\t-----Node List-----"
		nodes = db.getNodes()
	else:
		print "\t-----Node List in Session : %s-----" % args.NODES
		nodes = db.getNodes(args.NODES)
	for node in nodes:
		print node
else:
#------------------------------------------TESTING CODE---------------------------------------------------#	
	ses = 'testsession'
	dev1 = 'testdevx'
	dev2 = 'testdevy'
	dev3 = 'testdevz'
	dev4 = 'testdevu'
	cont1 = {'fName':'testfName', 'lName':'testlName', 'email':'test@email.com', 'phone':'18453384705'}
	badfName = 'bad1234'
	badlName = 'bad5678'
	bademail = 'email@@..1'
	badphone = '87asd123'
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
		print "\t(-) Failed to create session! Already Exists"
	print "\t(+) Session created!"
#---------------------------------------------------------------------------------------------------------#	
	print "(=) Testing Failure of createSession function"
	try:
		db.createSession(ses)
		print "\t(-) Failure of createSession Test Failed"
	except SessionError as se:
		print "\t(+) Failure of createSession Test Passed. Error Caught:", se.msg
#---------------------------------------------------------------------------------------------------------#	
	print "(=) Testing Failure of getSession function"
	try:
		db.getSession('invalidphrase')
		print "\t(-) Failure of getSession Test Failed"
	except SessionError as se:
		print "\t(+) Failure of getSession Test Passed. Error Caught:", se.msg
#---------------------------------------------------------------------------------------------------------#	
	print "(=) Setting period of %s to 1 day." % ses
	db.setSessionPeriod(ses, 1)
#---------------------------------------------------------------------------------------------------------#		
	print "(=) Testing Failure of setSessionPeriod function"
	try:
		db.setSessionPeriod(ses, 'invalid duration')
		print "\t(-) Failure of setSessionPeriod Test Failed"
	except ValueError as ve:
		print "\t(+) Failure of setSessionPeriod Test Passed. Error Caught:", ve.msg
#---------------------------------------------------------------------------------------------------------#	
	print "(=) Testing getSessions function"
	print "(=) List of all sessions"
	sessions = db.getSessions()
	for session in sessions:
		print session		
#---------------------------------------------------------------------------------------------------------#		
#---------------------------------------------------------------------------------------------------------#		
	print "(========)NODE FUNCTION TESTS(========)"
#---------------------------------------------------------------------------------------------------------#		
	print "(=) Creating nodes"
	d1 = db.createNode(dev1)
	d2 = db.createNode(dev2)
	d3 = db.createNode(dev3);	

	if d1 == -1 or d2 == -1 or d3 == -1:
		print "\t(-) Node Creation failed."
	else:
		print "\t(+) Nodes created."
#---------------------------------------------------------------------------------------------------------#	
	print "(=) Testing displayNodes function"
	print "(=) List of all nodes"
	nodes = db.getNodes()
	for node in nodes:
		print node
#---------------------------------------------------------------------------------------------------------#		
	print "(=) Testing creation of existing node"
	try:
		dx = db.createNode(dev1)
		print "\t(-) Existing Node Creation Test Failed."
	except:
		print "\t(+) Existing Node Creation Test Passed."
#---------------------------------------------------------------------------------------------------------#		
	print "(=) activateNode Test"	
	print "(=) activating device=%s" % dev2
	db.activateNode(dev2, ses)
	print "\t(+) Activated, printing all nodes in %s" % ses
	nodes = db.getNodes(ses)
	for node in nodes:
		print node
#---------------------------------------------------------------------------------------------------------#		
	print "(=) Assert Free Node Test"
	try:
		db.activateNode(dev2, ses)
		print "\t(-) Assert Free Node Test Failed"
	except NodeError as ne:
		print "\t(+) Assert Free Node Test Passed. Error Caught: ", ne.msg
#---------------------------------------------------------------------------------------------------------#			
	print "(=) freeNode Test"
	print "(=) freeing device=%s" % dev2
	db.freeNode(dev2)
	print "\t(+) Freed"
#---------------------------------------------------------------------------------------------------------#		
	print "(=) Check Node State Test"
	try:
		db.freeNode(dev2)
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
#---------------------------------------------------------------------------------------------------------#		
	print "(========)CONTACT FUNCTION TESTS(========)"
#---------------------------------------------------------------------------------------------------------#
	print "(=) Creating contact"
	contID = db.createContact(cont1['fName'], cont1['lName'], cont1['email'], cont1['phone'])
#---------------------------------------------------------------------------------------------------------#	
	print "(=) Testing Failure of createContact function"
	try:
		db.createContact(fName=badfName)
		print "\t(-) Failure of createContact Test Failed"
	except ContactError as ce:
		print "\t(+) Failure of createContact Test Passed. Error Caught:", ce.msg
	try:
		db.createContact(lName=badlName)
		print "\t(-) Failure of createContact Test Failed"
	except ContactError as ce:
		print "\t(+) Failure of createContact Test Passed. Error Caught:", ce.msg
	try:
		db.createContact(email=bademail)
		print "\t(-) Failure of createContact Test Failed"
	except ContactError as ce:
		print "\t(+) Failure of createContact Test Passed. Error Caught:", ce.msg
	try:
		db.createContact(phone=badphone)
		print "\t(-) Failure of createContact Test Failed"
	except ContactError as ce:
		print "\t(+) Failure of createContact Test Passed. Error Caught:", ce.msg
#---------------------------------------------------------------------------------------------------------#		
	print "(=) Testing findContact function"
	byID = db.findContact(cID=contID)
	if byID == contID:
		print "\t(+) Found contact by cID"
	else:
		print "\t(-) Could not find contact by cID"	
#---------------------------------------------------------------------------------------------------------#
	byInfo = db.findContact(fName=cont1['fName'], lName=cont1['lName'], email=cont1['email'], phone=cont1['phone'])
	if byInfo == contID:
		print "\t(+) Found contact by information"
	else:
		print "\t(-) Could not find contact by information"	
#---------------------------------------------------------------------------------------------------------#	
	print "(=) Testing assignSession function"
	db.assignSession(ses, fName=cont1['fName'], lName=cont1['lName'], email=cont1['email'], phone=cont1['phone'])
	db.unassignSession(ses)
	sessions = db.getSessions()
	for session in sessions:
		print session
#---------------------------------------------------------------------------------------------------------#
	print "(=) Testing assignNode function"
	db.assignNode(dev1, contID)
	db.unassignNode(dev1)
	nodes = db.getNodes()
	for node in nodes:
		print nodes
#---------------------------------------------------------------------------------------------------------#
	print "(=) Printing list of Contacts"
	contacts = db.getContacts()
	for contact in contacts:
		print contact
#---------------------------------------------------------------------------------------------------------#		
	print "(=) Cleaning up...."		
	db.deleteContact(contID)
	db.deleteNode(dev1)
	db.deleteNode(dev2)	
	db.deleteSession(ses)		
	db.close()	
#---------------------------------------------------------------------------------------------------------#	