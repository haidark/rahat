#!/usr/bin/env python

import DBhelper as db
import pymysql

class Manager:
	"""Manager Class - inherits from multiprocessing.Process
		Static Members:
			DBINFO tuple which contains database information - (host, user, pass, db)
		Members:
			host - Host IP address to listen on - string "xxx.xxx.xxx.xxx"
			port - Port number to listen on - int > 1000
		
		Functions:
			implements multiprocessing.Process.run() - can be multi process
			run() - socket code to bind to (IP, port) and accepts all clients
					spawns client thread to handle clients
	"""
	
	def __init__(self):
		pass
		
	
	