#!/usr/bin/env python

import DBhelper as db
import argparse
import pymysql
def DBconnect(host, user, pw):
	#connect to the DB
	conn = pymysql.connect(host, user, passwd, db='haramain2')
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
	
elif args.archive != None:
	#archive session
	(conn, cur) = DBconnect(host, user, pw)
	db.deleteSession(cur, args.archive)
	DBclose(conn, cur)
	print args.archive
	
elif args.node != None:
	#create a new node
	(conn, cur) = DBconnect(host, user, pw)
	db.createNode(cur, args.node)
	DBclose(conn, cur)
	print args.node
	
elif args.delete != None:
	#delete a node
	(conn, cur) = DBconnect(host, user, pw)
	DBclose(conn, cur)
	print args.delete
	
elif args.activate != None:
	#activate a node
	(conn, cur) = DBconnect(host, user, pw)
	db.activateNode(cur, agrs.activate[0], args.activate[1])
	DBclose(conn, cur)
	print args.activate
	
elif args.free != None:
	#free a node
	(conn, cur) = DBconnect(host, user, pw)
	db.freeNode(cur, args.free)
	DBclose(conn, cur)
	print args.free
	
elif args.SESSIONS == True:
	#list all sessions
	(conn, cur) = DBconnect(host, user, pw)
	db.displaySessions(cur)
	DBclose(conn, cur)
	print args.SESSIONS
	
elif args.NODES != None:
	#list nodes
	(conn, cur) = DBconnect(host, user, pw)
	if args.NODES == '0':
		db.displayNodes(cur)
	else:
		db.displayNodes(cur, args.NODES)
	DBclose(conn, cur)
	print args.NODES
	
else:
	parser.print_help()
