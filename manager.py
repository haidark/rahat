#!/usr/bin/env python

import DBhelper as db

import argparse
import pymysql
def DBconnect(host, user, pw):
	#connect to the DB
	conn = pymysql.connect(host, user, pw, db='haramain2')
	cur = conn.cursor()
	return (conn, cur)
	
def DBclose(conn, cur):
	cur.close()
	conn.close()

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

host = '127.0.0.1'
user='haidar'
pw='pin101'

if args.session != None:
	#create a new session
	(conn, cur) = DBconnect(host, user, pw)
	db.createSession(cur, args.session)
	DBclose(conn, cur)
	print "Created session with passphrase: " + args.session
	
elif args.archive != None:
	#archive session
	(conn, cur) = DBconnect(host, user, pw)
	db.deleteSession(cur, args.archive)
	DBclose(conn, cur)
	print "Deleted session with passphrase: " + args.archive
	
elif args.node != None:
	#create a new node
	(conn, cur) = DBconnect(host, user, pw)
	db.createNode(cur, args.node)
	DBclose(conn, cur)
	print "Created node with device ID: " + args.node
	
elif args.delete != None:
	#delete a node
	(conn, cur) = DBconnect(host, user, pw)
	db.deleteNode(cur, args.delete)
	DBclose(conn, cur)
	print "Deleted node with device ID: " + args.delete
	
elif args.activate != None:
	#activate a node
	(conn, cur) = DBconnect(host, user, pw)
	db.activateNode(cur, agrs.activate[0], args.activate[1])
	DBclose(conn, cur)
	print "Added node with device ID: " + args.activate[0] + " to session with passphrase: " + args.activate[1]
	
elif args.free != None:
	#free a node
	(conn, cur) = DBconnect(host, user, pw)
	db.freeNode(cur, args.free)
	DBclose(conn, cur)
	print "Freed node with device ID: " + args.free
	
elif args.SESSIONS == True:
	#list all sessions
	(conn, cur) = DBconnect(host, user, pw)
	print "-----Session List-----"
	db.displaySessions(cur)
	DBclose(conn, cur)
	
elif args.NODES != None:
	#list nodes
	(conn, cur) = DBconnect(host, user, pw)
	if args.NODES == '0':
		print "-----Node List-----"
		db.displayNodes(cur)
	else:
		print "-----Node List in Session : %s-----" % args.NODES
		db.displayNodes(cur, args.NODES)
	DBclose(conn, cur)
	
else:
	#run a test of each function
	#variables
	ses = 'testsession'
	dev1 = 'testdevx'
	dev2 = 'testdevy'
	dev3 = 'testdevz'
	
	print "(========)Testing all DB managing functions(========)"
	print "(=) Connecting to the DB..."
	(conn, cur) = DBconnect(host,user,pw)
	print "\t(+) Connected!"
	
	print "(========)SESSION FUNCTION TESTS(========)"	
	print "(=) Creating a new session called '%s'" % ses
	try:
		db.createSession(cur, ses)
	except db.SessionError as se:
		pass
	print "\t(+) Session created!"
	print "(=) Testing Failure of createSession function"
	try:
		db.createSession(cur, ses)
		print "\t(-) Failure of createSession Test Failed"
	except db.SessionError as se:
		print "\t(+) Failure of createSession Test Passed. Error Caught:", se.msg
	
	
	print "(========)NODE FUNCTION TESTS(========)"
	print "(=) Creating nodes"
	d1 = db.createNode(cur, dev1, ses)
	d2 = db.createNode(cur, dev2)
	d3 = db.createNode(cur, dev3);
	
	
	#check if everything went well
	if d1 == -1 or d2 == -1 or d3 == -1:
		"\t(-) Node Creation failed! Printing list of all Nodes."
		db.displayNodes(cur)
	else:
		print "\t(+) Nodes created! Testing displayNodes function"
		print "(=) List of all nodes"
		db.displayNodes(cur)
		print "(=) List of all nodes in session=%s" % ses
		db.displayNodes(cur, ses)
	
	print "(=) Testing creation of existing node"
	dx = db.createNode(cur, dev1, ses)
	if dx == d1:
		"\t(+) Existing Node Creation Test Passed. nIDs are the same. Warning printed"
	else:
		"\t(-) Existing Node Creation Test Failed. nIDs are not the same. Printing list of all Nodes."
		db.displayNodes(cur)
	
	print "(=) activateNode Test"
	
	print "(=) activating device=%s" % dev2
	db.activateNode(cur, dev2, ses)
	print "\t(+) Activated, printing all nodes in %s" % ses
	db.displayNodes(cur, ses)
	
	print "(=) Assert Free Node Test"
	try:
		db.activateNode(cur, dev2, ses)
		print "\t(-) Assert Free Node Test Failed"
	except db.NodeError as ne:
		print "\t(+) Assert Free Node Test Passed. Error Caught: ", ne.msg
		
	print "(=) freeNode Test"

	print "(=) freeing device=%s" % dev1
	db.freeNode(cur, dev1)
	print "\t(+) Freed, printing all nodes"
	db.displayNodes(cur)
	
	print "(=) Check Node State Test"
	try:
		db.freeNode(cur, dev1)
		print "\t(-) Check Node State Test Failed"
	except db.NodeError as ne:
		print "\t(+) Check Node State Test Passed. Error Caught: ", ne.msg
	
	print "(=) deleteNode Test"
	
	print "(=) deleting device=%s" % dev3
	db.deleteNode(cur, dev3)
	
	print "(=) deleting non-existent device."
	try:
		db.deleteNode(cur, 'devu')
		print "\t(-) deleteNode Test Failed."
	except db.NodeError as ne:
		print "\t(+) deleteNode Test Passed. Error Caught: ", ne.msg
	
	print "(=) cleaning up."
	
	db.deleteNode(cur, dev1)
	db.deleteNode(cur, dev2)
	
	db.deleteSession(cur, ses)
		
	db.displayNodes(cur)	
	DBclose(conn, cur)	
		
		
		
		
	#parser.print_help()
