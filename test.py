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
t.func1()

t.func2(4)