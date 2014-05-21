class testClass:
	def __init__(self):
		self.var1 = 1
		self.var2 = 2
		
	def func1(self):
		print self.var1
		print self.var2
		self.func2(3)
		testClass.func3(5)
	
	def func2(self, arg1):
		print arg1
		print self.var1
		
	def func3(arg2):
		print arg2
		
t = testClass()

import smtplib

sender = 'from@fromdomain.com'
receivers = ['to@todomain.com']

message = """From: From Person <from@fromdomain.com>
To: To Person <to@todomain.com>
Subject: SMTP e-mail test

This is a test e-mail message.
"""

try:
   smtpObj = smtplib.SMTP('localhost')
   smtpObj.sendmail(sender, receivers, message)         
   print "Successfully sent email"
except SMTPException:
   print "Error: unable to send email"
