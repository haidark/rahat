from multiprocessing import Process
from DBManager import DBManager, ContactError
import logging
import smtplib

class Reporter(Process):
	"""Reporter class receives Alert objects from a Queue and dispatches proper message to contacts
		Static Members:
			None
		Members:
			queue - Queue that this reporter is listening to
			reporterID - ID for this reporter
			logger - handle for Reporter logger
		Functions:
			__init__(queue, reporterID)
			run() - runs reporting loop, gets alerts and sends out emails and sms
			sendEmail(email, alert) - sends an email with data from Alert object
			sendSms(sms, alert) - sends an sms with data from Alert object
	"""
	def __init__(self, queue, reporterID=0):
		Process.__init__(self)
		self.queue = queue
		self.reporterID = reporterID
		self.logger = logging.getLogger("reporter")
		
	def run(self):
		#run until forced to stop
		while True:
			#block until a new alert object appears on the queue
			alert = self.queue.get()
			#if alert.contactID exists
			if alert.contactID is not None:
				#try to find the contact information for the alert object's contactID
				try:
					db = DBManager()
					contact = db.findContact(cID=alert.contactID)
					db.close()
					#send the alert using the provided communication types
					self.sendAlert(contact, alert)
				except ContactError as ce:
					self.logger.info( str(self.reporterID) + ": Contact with ID: %s was not found" % str(alert.contactID) )
	
	def sendAlert(self, contact, alert):
		#dictionary which matches communication type to its handler function
		commFuncs={ 'email':self.sendEmail,
					'sms':self.sendSms }
		#for every communication type
		for type in commFuncs:
			#if its column for this contact is not NULL
			if contact[type] is not None:
				#call its handler function and pass it the contact info and the alert info
				commFuncs[type](contact, alert)
	
	def sendEmail(self, contact, alert):
		#get address of recipient 
		address = contact['email']
		#set sender and receivers addresses
		sender = 'alerts@rahat.com'
		receivers = [address]
		#get the users full name
		flName = [name for name in [contact['fName'], contact['lName']] if not name==None]
		#if any part of the name is available
		if flName:
			flName = ' '.join(flName)
		#if it is not available, set it to their email
		else:
			flName=address
		message = """From: Reporter <%s>
		To: %s <%s>
		Subject: %s

		%s,
		%s
		This is an alert from the Rahat Project.
		""" % (sender, flName, address, alert['title'], flName, alert['message'])
		
		try:
		   smtpObj = smtplib.SMTP('localhost')
		   smtpObj.sendmail(sender, receivers, message)         
		   self.logger.info( str(self.reporterID) + ":(+) Sent email Alert to %s at %s." % (flName, address) )
		except SMTPException:
		   self.logger.info( str(self.reporterID) + ":(-) Unable to send email Alert to %s at %s." % (flName, address) )
		
		
	def sendSms(self, contact, alert):
		self.logger.info( str(self.reporterID) + ": Sent Alert to %s at %s." % (contact['fName'], contact['sms']) ) 
		
	
				
