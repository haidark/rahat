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
print """Hello 
asdf
	asdasd
			asdasd
			
"""
import smtplib

email = input("Enter email address: ")
sender = 'from@fromdomain.com'
receivers = [email]

message = """From: From Person <from@fromdomain.com>
To: To Person <%s>
Subject: SMTP e-mail test

This is a test e-mail message.
""" % email

try:
   smtpObj = smtplib.SMTP('localhost')
   smtpObj.sendmail(sender, receivers, message)         
   print "Successfully sent email"
except SMTPException:
   print "Error: unable to send email"
