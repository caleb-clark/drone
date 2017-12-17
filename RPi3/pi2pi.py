

import ConfigParser
from shutil import copyfile
import socket
import sys
from random import randint
import json
from controller import *
import math
import time
from drone import *

'''
JSON Message fields:
0: Vertical Power Leve [float]
1: Rotational Power  [float]
2: Lateral Power [float]
3: Forward Power [float]
4: Mode [int]

'''
'''
Modes

'''



class pi2pi:

	def __init__(self, isBaseStation, droneConnectionStr='', portNum=55655, bsAddr="localhost", hostName="localhost", default_filename = 'attributes_default.ini', curr_filename='attributes_curr.ini', changesThreshold=20):
		self.isBaseStation = isBaseStation
		self.hostName = hostName
		self.portNum = portNum
		self.bsAddr = bsAddr 
		self.socket = None
		self.buddy = None
		self.currMode = 0
		self.clientSocket = None
		self.clientAddress = None
		if isBaseStation:
			self.buddy = controller(5.117)
		else:
			self.buddy = droneStats(droneConnectionStr) # put in stuff for drone() class


		self.powerLevels = {
			0: 0,
			1: 50,
			2: 50,
			3: 50
		}

		self.powers = {
			'VERTICAL': 0,
			'ROTATIONAL': 1,
			'LATERAL': 2,
			'FORWARD':3
		}

		self.powerCodes = {
			0: 'VERTICAL',
			1: 'ROTATIONAL',
			2: 'LATERAL',
			3: 'FORWARD'
		}

		self.modes = {
			'LANDED': 0,
			'TAKEOFF': 1,
			'LANDING': 2,
			'IDLE': 3,
			'FLYING': 4,
			'CRASH': 5
		}

		self.modeCodes = {
			0: 'LANDED',
			1: 'TAKEOFF',
			2: 'LANDING',
			3: 'IDLE',
			4: 'FLYING',
			5: 'CRASH'
		}

		self.socket = None

	def loop(self):
		if isBaseStation:
			baseStationLoop()
		else:
			mobileUnitLoop()

	def changeMode(self, mode):

		if not (mode in self.modeCodes):
			return False
		if self.isBaseStation:
			if mode == 5:
				self.currMode == 5
				return True
					
			if self.currMode == 0:
				if mode == 1:
					self.currMode == mode:
					return True
				
			elif self.currMode == 1:
				if mode == 3:
					self.currMode = mode
					return True
				
			elif self.currMode == 2:
				if mode == 0 or mode == 3:
					self.currMode == mode
					return True
				
			elif self.currMode == 3:
				if mode == 1 or mode == 2 or mode == 4:
					self.currMode = mode
					return True
				
			elif self.currMode == 4:
				if mode == 3:
					self.currMode = mode
					return True
			elif self.currMode == 5:
				return False
			else:
				return False
			return False
		else:
			return True



	def adjustPower(self, axisDict):


		for i in axisDict:
			if not (i in self.powerCodes) && i != 4:
				print(str(i) + ' not a valid power axis code!')
				return False


		if self.isBaseStation:
			for i in axisDict:
				if i == 4 or i == 1:
					continue #TODO: figure out rotational power

				if i == 0:
					self.buddy.verticalPower(axisDict[i])
				elif i == 1:
					self.buddy.rotationalPower(axisDict[i])
				elif i == 2:
					self.buddy.lateralPower(axisDict[i])
				elif i == 3:
					self.buddy.forwardPower(axisDict[i])
		else:
			return axisDict

	def sendDict(self, dict_):
		if self.isBaseStation:
			data_string = json.dumps(dict_) #data serialized
			self.clientSocket.send(data_string)
		else:	
			data_string = json.dumps(dict_) #data serialized
			self.socket.send(data_string)
			return self.socket.recv(1024)
	
			


	def jsonToDict(self, jsonStr):
		return json.loads(jsonStr)




	def maintainVelocity(self,axis):

		toReturn = [self.powerLevels[0],self.powerLevels[1],self.powerLevels[2],self.powerLevels[3]]


		if len(axis) != 4:
			return toReturn

		for i in range(0,len(axis)):
			if axis[i] and i != 1:
				currAxisVelo = None
				if i == 0:
					currAxisVelo = self.buddy.getVerticalVelocity()
				elif i == 1:
					#currAxisVelo = self.buddy.getRotationalVelocity()
					continue
				elif i == 2:
					currAxisVelo = self.buddy.getLateralVelocity()
				elif i == 3:
					currAxisVelo = self.buddy.getForwardVelocity()
				newPowerLevel = toReturn[i]

				if math.fabs(currAxisVelo) > 0.02:
					if currAxisVelo < 0:
						if newPowerLevel >= 50:
							newPowerLevel = 49
						elif newPowerLevel > 35:
							newPowerLevel -= 1
					else:
						if newPowerLevel <= 50:
							newPowerLevel = 51
						elif newPowerLevel < 65:
							newPowerLevel += 1


				toReturn[i] = newPowerLevel

		return toReturn



	def takeOff(self):
		time.sleep(3)
		
		changesDict = {}

		maintainArr = [False,True,True,True]

		changesDict[0] = 51
		self.powerLevels[0] = 51

		sendDict(changesDict)




		start_ = time.time()

		while (time.time() - start_) < 1.0:
			changesDict2 = {}
			newPowerLevels = maintainVelocity(maintainArr)
			changesDict2[1] = newPowerLevels[1]
			self.powerLevels[1] = newPowerLevels[1]
			
			changesDict2[2] = newPowerLevels[2]
			self.powerLevels[2] = newPowerLevels[2]

			changesDict2[3] = newPowerLevels[3]
			self.powerLevels[3] = newPowerLevels[3]

			sendDict(changesDict2)


		changesDict[0] = 50
		self.powerLevels[0] = 50
		changesDict[4] = 3
		self.currMode = 3
		sendDict(changesDict)


	def land(self):
		time.sleep(3)
		
		changesDict = {}

		maintainArr = [False,True,True,True]

		changesDict[0] = 49
		self.powerLevels[0] = 49

		sendDict(changesDict)




		start_ = time.time()

		while (time.time() - start_) < 1.0:
			changesDict2 = {}
			newPowerLevels = maintainVelocity(maintainArr)
			changesDict2[1] = newPowerLevels[1]
			self.powerLevels[1] = newPowerLevels[1]
			
			changesDict2[2] = newPowerLevels[2]
			self.powerLevels[2] = newPowerLevels[2]

			changesDict2[3] = newPowerLevels[3]
			self.powerLevels[3] = newPowerLevels[3]
			sendDict(changesDict2)


		changesDict[0] = 10
		self.powerLevels[0] = 10
		changesDict[4] = 0
		self.currMode = 0
		sendDict(changesDict)	
	def idle(self, time_):
		maintainArr = [True,True,True,True]
		while (time.time() - start_) < time_:
			changesDict2 = {}
			newPowerLevels = maintainVelocity(maintainArr)

			changesDict2[1] = newPowerLevels[1]
			self.powerLevels[1] = newPowerLevels[1]

			changesDict2[1] = newPowerLevels[1]
			self.powerLevels[1] = newPowerLevels[1]
			
			changesDict2[2] = newPowerLevels[2]
			self.powerLevels[2] = newPowerLevels[2]

			changesDict2[3] = newPowerLevels[3]
			self.powerLevels[3] = newPowerLevels[3]
			sendDict(changesDict2)
		
		changesDict = {4:2}
		
		sendDict(changesDict)
		self.currMode = 2

	def mobileUnitLoop(self):
		
		while not self.buddy.armed():
			continue

		self.socket = socket.socket()         # Create a socket object

		address = ''

		print(self.bsAddr)

		if self.bsAddr == "localhost":
			address = socket.gethostname()
		else:
			address = self.bsAddr
		
		self.socket.connect((address, self.portNum))

		msg = self.socket.recv(1024)

		if msg != 'HOWDY':
			print(msg)
			self.socket.send('FUCK OFF')
			self.socket.close()
			exit()

		'''
		TODO1: Implement vertical limiting on takeoff,
			  vertical limiting = distance/velocity/timeout
		TODO2: Receive info from base station about what
			  part of the request could be fulfilled and
			  take action based on that
		'''

		while True:

			changesDict = {}

			if self.currMode == 0:
				if powerLevels[0] == 0:
					changesDict[0] = 10
					powerLevels[0] = 10 #TODO2 wait for feedback before changing
				if powerLevels[0] > 0:
					changesDict[4] = 1
			elif self.currMode == 1:
				self.takeOff()
				continue
			elif self.currMode == 2:
				self.land()
				continue
			elif self.currMode == 3:
				self.idle()
				continue



			sendDict(changesDict)
			msg = self.socket.recv(1024)

			if msg == 'ACK':
				continue
			else:
				continue # TODO2 get feedback

			
	def baseStationLoop(self):
		
		self.socket = socket.socket() # Create a socket object
		
		self.hostName = socket.gethostname()   # Get local machine name
					
		self.socket.bind((self.hostName, self.portNum))        # Bind to the port

		self.socket.listen()                   # Now wait for client connection.
		
		self.clientSocket, self.clientAddress = self.socket.accept()      # Establish connection with client.

		self.clientSocket.send('HOWDY')

		while True:
			
			jsonStr = self.clientSocket.recv(1024)
			
			changesDict = jsonToDict(jsonStr)

			adjustPower(changesDict)

			#mode change
			if 4 in changesDict:
				if not changeMode(changesDict[4]):
					pass #TODO2 - feedback stuff
				else:
					pass #TODO2

			self.socket.send('ACK')


