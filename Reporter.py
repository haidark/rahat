from multiprocessing import Process
from DBManager import DBManager, ContactError
import logging

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
			self.logger.debug(str(alert))
			#try to find the contact information for the alert object's contactID
			try:
				db = DBManager()
				contact = db.findContact(cID=alert.contactID)
				db.close()
				email = contact['email']
				sms = contact['sms']
				#if contact has an email address on file send an email to that address
				if email is not None:
					self.sendEmail(email, alert) 
				#if contact has an sms number on file send an sms to that number
				if sms is not None:
					self.sendSms(sms, alert)
			except ContactError as ce:
				self.logger.info( str(self.reporterID) + ": Contact with ID: %s was not found" % str(alert.contactID) )
				
	def sendEmail(self, email, alert):
		self.logger.info( str(self.reporterID) + ": Sent Alert to %s." % str(email) ) 
		
	def sendSms(self, sms, alert):
		self.logger.info( str(self.reporterID) + ": Sent Alert to %s." % str(sms) ) 
		
		