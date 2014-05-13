#!/usr/bin/env python
from threading import Thread
import socket

##########################################################################
# Python Client Thread
##########################################################################
class ClientThread(Thread):
	def __init__(self, HOST, PORT, devID, locTime, lat, lon, waitTime):
		Thread.__init__(self)
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.HOST = HOST
		self.PORT = PORT		
		self.msg = self.packLocation(devID, locTime, lat, lon)
		self.waitTime = waitTime
		
	def run(self):
		self.s.connect((self.HOST, self.PORT))
		self.s.sendall(self.msg)
		self.s.close()
		
	def packLocation(self, devID, locTime, lat, lon):
		return self.preLen(devID) + self.preLen(locTime) + self.preLen(lat) + self.preLen(lon)
		
	def preLen(self, string):
		#prepends length of the string to the string.
		
		#if length is less than 10, pad with leading zero
		if len(string) < 10:
			length = '0' + str(len(string))
		else:
			length = str(len(string))
		
		#if length of string is more than 99 characters, the string is sent piecemeal
		if len(string) <= 99:
			return length+string
		else:
			return str(99)+string[0:98]+'~'+preLen(string[98:])

HOST = 'haidarkhan.no-ip.org'
PORT = 1060
devID = 'python-script'
locTime = '1991-11-04 00:00:01'
lat = '0.0'
lon = '0.0'

for i in range(0,5):
	cThread = ClientThread(HOST, PORT, devID, locTime, lat, lon, 30-i)
	cThread.run()


