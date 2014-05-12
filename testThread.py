from threading import Thread
from time import sleep

class TestThread(Thread):
	def __init__(self):
		Thread.__init__(self)
		
	def run(self):
		print "Test Thread is running"
			
t = TestThread()

t.start()

if not t.is_alive():
	t.start()
# except RuntimeError as re:
	# print re