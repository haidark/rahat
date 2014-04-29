##########################################################################
##########################################################################
##################### Exception Definitions ##############################
##########################################################################
##########################################################################

class Error(Exception):
	"""Base class for exceptions in this module."""
	pass
	
class NodeError(Error):
	"""Exception raised for errors related to nodes.

	Attributes:
	devID -- input devID for which node error occurred
	msg  -- explanation of the error
	"""
	
	def __init__(self, devID, msg):
		self.devID = devID
		self.msg = msg
	
	#Error Types
	DNE = "Node Does Not Exist"
	AE = "Node Already Exists"
	ACT = "Node is Active"
	FRE = "Node is Free"
	
class SessionError(Error):
	"""Exception raised for errors related to sessions.

	Attributes:
	session -- input session for which session error occurred
	msg  -- explanation of the error
	"""	
	
	def __init__(self, session, msg):
		self.session = session
		self.msg = msg
	
	#Error types
	DNE = "Session Does Not Exist"
	AE = "Session Already Exists"
		
class FieldError(Error):
	"""Exception raised for errors related to invalid fields.

	Attributes:
	field -- input field for which field error occurred
	msg  -- explanation of the error
	"""
	
	def __init__(self, field, msg):
		self.field = field
		self.msg = msg
	
	#Error types
	IP = "Invalid Phrase for Session"
	ID = "Invalid devID for Node"