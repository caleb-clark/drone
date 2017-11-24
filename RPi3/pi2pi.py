

import ConfigParser
from shutil import copyfile
import socket
import sys
from random import randint
import json


''' Implement dictionary to keep track of which attributes have changed '''

class pi2pi:

	def __init__(self, isBaseStation, recoveryMode = False,portNum=55655, bsAddr="localhost", hostName="localhost", default_filename = 'attributes_default.ini', curr_filename='attributes_curr.ini', changesThreshold=20):

		self.isBaseStation = isBaseStation
		self.hostName = hostName
		self.portNum = portNum
		self.bsAddr = bsAddr 
		self.socket = None
		self.status = 0
		self.attribute_list = []
		self.attributes = {}
		self.attributes_changes = {}
		self.config_default = ConfigParser.ConfigParser()
		self.config_curr = ConfigParser.ConfigParser()
		self.config_section = 'attributes'
		self.config_has_changed = False
		self.default_filename = default_filename
		self.curr_filename = curr_filename
		self.recoveryMode = recoveryMode
		self.changesSinceBackup = 0
		self.changesThreshold = changesThreshold

		
		self.readConfig(self.default_filename,self.config_section, self.config_default)

		if not self.recoveryMode:
			copyfile(self.default_filename, self.curr_filename)
		# PUT IN RECOVER MODE STUFF




	def readConfig(self, fileName, section, parser):
	    parser.read('./attributes_default.ini')
	    self.attribute_list = parser.options(section)
	    for attr in self.attribute_list:
	        try:
	            self.attributes[attr] = parser.get(section, attr)
	            self.attributes_changes[attr] = False

	        except:
	            print("exception on %s!" % attr)
	            self.attributes[attr] = None
	    print(self.attributes)
	    
	def writeConfig(self, attr, new_val):
		with open(self.curr_filename) as cfgfile:
			self.config_curr.add_section(self.config_section)
			self.config_curr.set(self.config_section,attr,new_val)
			self.config_curr.write(cfgfile)
			

	def loop(self):
		if self.isBaseStation:
			self.baseStationLoop()
		else:
			self.mobileUnitLoop()

	def getHostName(self):

		return self.hostName

	def getPortNum(self):
		return self.portNum

	def getIsBaseStation(self):
		return self.isBaseStation

	def getStatus(self):
		return self.status

	def setStatus(self, status_code):
		if not self.getIsBaseStation():
			self.status = status_code
			return 0
		else:
			print('Cannot set status')
			return -1
	def getAttribute(self, attr):
		return self.attributes[attr]

	def setAttribute(self, attr, new_val):
		if self.attributes[attr] != None:
			self.attributes[attr] = new_val
			self.attributes_changes[attr] = True
			self.changesSinceBackup += 1
			if self.changesSinceBackup >= self.changesThreshold:
				synchronization()

	def synchronization(self):
		#remember to reset changes counter!!
		pass

	def baseStationLoop(self):
		self.socket = socket.socket() # Create a socket object
		self.hostName = socket.gethostname()   # Get local machine name
					
		self.socket.bind((self.hostName, self.portNum))        # Bind to the port

		self.socket.listen(5)                   # Now wait for client connection.
		
		c, addr = self.socket.accept()      # Establish connection with client.
		print 'Got connection from', addr
		c.send('HELLO')
		
		msg = c.recv(1024)
		print(msg)
		if msg == 'HELLO':
			print('here')
			while True:
				print('loop')
				c.send('READY')
				data_string = c.recv(1024)
				print(data_string)
				data_loaded = json.loads(data_string) #data loaded

				print(data_loaded['000'])
				break
		c.close()                 # Close the connection

	def mobileUnitLoop(self):
		self.socket = socket.socket()         # Create a socket object
		address = ''
		print(self.bsAddr)
		if self.bsAddr == "localhost":
			print('blah blah')
			address = socket.gethostname()
		else:
			address = self.bsAddr
		print(address)
		print('\n')
		self.socket.connect((address, self.portNum))

		msg = self.socket.recv(1024)
		print(msg)
		if msg == 'HELLO':
			self.socket.send('HELLO')
			msg = self.socket.recv(1024)
			print(msg)
			if msg == 'READY':
				test_dict = {}
				test_dict['000'] = 000
				print('test_dict')
				print(test_dict)

				data_string = json.dumps(test_dict) #data serialized
				print(data_string)
				self.socket.send(data_string)

		self.socket.close                     # Close the socket when done

portNum_ = int(sys.argv[1])

if len(sys.argv) > 2:
	q = pi2pi(True, portNum=portNum_)
	q.loop()
else:
	q = pi2pi(False, portNum=portNum_)
	q.loop()