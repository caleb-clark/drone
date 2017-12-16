import threading
import time

# Import the MCP4725 module.
import Adafruit_MCP4725
from wiringSetup import *
from cmd import *
import serial
import threading


class controller:


	def __init__(self, dacInputVoltage):
		# Create a DAC instance.
		self.dac = Adafruit_MCP4725.MCP4725() # reference to DAC
		self.dacInputVoltage = dacInputVoltage #input to the DAC 3.3 V or 5 V
		self.enablePins = [7,11,13,15]
		#self.RPi0 = pi2pi()
		self.armPin = 29
		
		''' Default values for joystick axis voltage levels '''
		self.defaultVerticalVoltage = 0.08 # Volts
		self.defaultRotationalVoltage = 1.67 # Volts
		self.defaultLateralVoltage = 1.67 # Volts
		self.defaultForwardVoltage = 1.67 # Volts

		''' Default values for joystick axis voltage levels '''
		self.defaultVerticalPower = 50 # %
		self.defaultRotationalPower = 50 # %
		self.defaultLateralPower = 50 # %
		self.defaultForwardPower = 50 # %

		''' Minimum and maximum voltages to write to joysticks '''
		self.minVoltage = 0.08 # minimum voltage to write to joystick axis
		self.maxVoltage = 3.42 # maximum voltage to write to joystick axis

		self.currVerticalVoltage = 0.0
		self.currRotationalVoltage = 0.0
		self.currLateralVoltage = 0.0
		self.currForwardVoltage = 0.0

		self.currVerticalPower = 0
		self.currRotationalPower = 0
		self.currLateralPower = 0
		self.currForwardPower = 0

		self.verticalMultiplier = 1.0
		self.rotationalMultiplier = 1.0
		self.lateralMultiplier = 1.0
		self.forwardMultiplier = 1.0

		self.multiplierLock = threading.Lock()
		self.powerChangeLock = threading.Lock()



		initPins()
		temp_ = self.enablePins
		temp_.append(self.armPin)
		setup(temp_, [])




	def setDefaultPowerLevels(self):
		''' Reset joysticks to their default values '''
		if self.verticalPower(self.defaultVerticalPower) == -1:
			print ('Idle failed: Could not set vertical power levels')
			return -1
		if self.rotationalPower(self.defaultRotationalPower) == -1:
			print ('Idle failed: Could not set rotational power levels')
			return -1
		if self.lateralPower(self.defaultLateralPower) == -1:
			print ('Idle failed: Could not set lateral power levels')
			return -1
		if self.forwardPower(self.defaultForwardPower) == -1:
			print ('Idle failed: Could not set forward power levels')
			return -1
	def setLiftOffPowerLevels(self):
		''' Reset joysticks to their default values '''
		if self.verticalPower(0) == -1:
			print ('Lift off failed: Could not set vertical power level for lift off')
			return -1
		if self.rotationalPower(self.defaultRotationalPower) == -1:
			print ('Lift off failed: Could not set rotational power level for lift off')
			return -1
		if self.lateralPower(self.defaultLateralPower) == -1:
			print ('Lift off failed: Could not set lateral power level for lift off')
			return -1
		if self.forwardPower(self.defaultForwardPower) == -1:
			print ('Lift off failed: Could not set forward power level for lift off')
			return -1

	def prepareForLiftOff(self):

		# All drone system checks disabled so we just need to set joysticks to default
		# and check if the drone is armable

		# place the joysticks at appropriate power for liftoff 

		self.setLiftOffPowerLevels()

		# see if we can arm the drone

		if not self.RPi0.isArmable():
			print('Lift off failed: Drone not armable')
			return -1

		return 0

	def liftOffNoComms(self):

		self.setLiftOffPowerLevels()

		print('Attempting to arm drone...')
		if self.armDrone() == -1:
			print('Lift off failed: Could not arm drone')
			return -1

		print('done')

		print('Prepare for lift off!')

		while self.currVerticalPower < 50:
			verticalPower(self.currVerticalPower + 1)
			time.sleep(0.02)

		ascent_power = 55

		self.verticalPower(ascent_power)

		time.sleep(2)

		self.setDefaultPowerLevels()

	def land(self, configDict, attr):
		''' 
		The land function assumes that the ground is clear but must
		maintain communication with the RPi0 to coordinate landing
		
		'''

		print('Landing procedure initiated, getting permission to land...')

		# hault all movement of the vehicle

		setDefaultPowerLevels()
		verticalPower(45)
		while configDict[attr] == 1 or configDict[attr] == '1':
			time.sleep(0.1)



	def verticalPower(self, power):
		'''
		Set the vertical power of the drone
		power: % of power from 0 to 100 %

		'''

		raw_voltage_val = self.powerToVoltage(power)
		if power < 0 or power > 100:
			print('Invalid power value')
			return -1
		else:
			self.powerChangeLock.acquire()
			self.enable(0)
			self.multiplierLock.acquire()
			voltage_dac_val = (4096.0*(3.42/5.0) - self.powerToDacVal(power)*(3.42/5.0))*self.verticalMultiplier
			self.multiplierLock.release()
			self.dac.set_voltage(int(voltage_dac_val))
			
			self.currVerticalPower = power
			self.currVerticalVoltage = (voltage_dac_val/4096.0)*5.0
			self.powerChangeLock.release()
			return 0
	def fbf(self):
		self.verticalPower(50.5)
		time.sleep(0.1)
		self.verticalPower(0)

	def rotationalPower(self, power):
		''' 
		Set the power of rotation of the drone
		power: % of power from 0 to 100 %

		'''		
		raw_voltage_val = self.powerToVoltage(power)
		if power < 0 or power > 100:
			print('Invalid power value')
			return -1
		elif raw_voltage_val > self.maxVoltage:
			print('Requested value exceeds the joysticks maximum voltage (you might want to switch to 3.3 V input to the DAC)')
			return -1
		else:
			self.powerChangeLock.acquire()
			self.enable(1)
			self.multiplierLock.acquire()
			voltage_dac_val = (4096.0*(3.42/5.0) - self.powerToDacVal(power)*(3.42/5.0))*self.rotationalMultiplier
			self.multiplierLock.release()
			self.dac.set_voltage(int(voltage_dac_val))
			
			self.currRotationalPower = power
			self.currRotationalVoltage = (voltage_dac_val/4096.0)*5.0
			self.powerChangeLock.release()
			return 0


	def lateralPower(self, power):
		'''
		Set the power of the lateral (left and right) direction
		power: % of power from 0 to 100 %

		'''		
		raw_voltage_val = self.powerToVoltage(power)
		if power < 0 or power > 100:
			print('Invalid power value')
			return -1
		elif raw_voltage_val > self.maxVoltage:
			print('Requested value exceeds the joysticks maximum voltage (you might want to switch to 3.3 V input to the DAC)')
			return -1
		else:
			self.powerChangeLock.acquire()
			self.enable(2)
			self.multiplierLock.acquire()
			voltage_dac_val = ((4096.0*(3.42/5.0) - self.powerToDacVal(power)*(3.42/5.0)))*self.lateralMultiplier
			self.multiplierLock.release()
			self.dac.set_voltage(int(voltage_dac_val))
			
			self.currLateralPower = power
			self.currLateralPower = (voltage_dac_val/4096.0)*5.0
			self.powerChangeLock.release()
			return 0


	def forwardPower(self, power):
		'''
		Set the power of the forward/backward direction
		power: % of power from 0 to 100 %

		'''		
		raw_voltage_val = self.powerToVoltage(power)
		if power < 0 or power > 100:
			print('Invalid power value')
			return -1

		else:
			self.powerChangeLock.acquire()
			self.enable(3)
			self.multiplierLock.acquire()
			voltage_dac_val = (4096.0*(3.42/5.0) - self.powerToDacVal(power)*(3.42/5.0))*self.forwardMultiplier
			self.multiplierLock.release()
			self.dac.set_voltage(int(voltage_dac_val))
			
			self.currForwardPower = power
			self.currForwardVoltage = (voltage_dac_val/4096.0)*5.0
			self.powerChangeLock.release()
			return 0


	def powerToVoltage(self, power):
		''' 
		Convert the value of a % power value to a voltage value
		NOTE: This value depends on the input to the DAC

		'''
		return ((power/100.0) * self.dacInputVoltage)

	def powerToDacVal(self, power):
		'''
		Convert a percent power value to a DAC value (0 - 4096)

		'''
		val = ((power/100.0) * 4096.0)
		print(val)
		return val
	

	def enable(self,p):
		if p < 0 or p > 3:
			print('invalid')
			return
		if p == 0:
			turnOff(self.enablePins[0])
			turnOn(self.enablePins[1])
			turnOn(self.enablePins[2])
			turnOn(self.enablePins[3])
		elif p == 1:
			turnOn(self.enablePins[0])
			turnOff(self.enablePins[1])
			turnOn(self.enablePins[2])
			turnOn(self.enablePins[3])
		elif p == 2:
			turnOn(self.enablePins[0])
			turnOn(self.enablePins[1])
			turnOff(self.enablePins[2])
			turnOn(self.enablePins[3])
		elif p == 3:
			turnOn(self.enablePins[0])
			turnOn(self.enablePins[1])
			turnOn(self.enablePins[2])
			turnOff(self.enablePins[3])

	def arm(self):
		turnOn(self.armPin)
		time.sleep(3)
		turnOff(self.armPin)
		return 0
	def calibrate(self):
		while True:
			print('Calibrating 0th DAC')
			
			self.verticalPower(50)
			should_be = 0.5*3.42
			actual = raw_input("Should be " + str(should_be) + " V, what do you see? ")
			self.multiplierLock.acquire()
			self.verticalMultiplier = self.verticalMultiplier*float(should_be)/float(actual)
			self.multiplierLock.release()
			self.verticalPower(50)
			check = raw_input("Does that look good? 1=yes, 0=no: ")
			if check == '1' or check == "1":
				break
			print('\n')
		while True:
			print('Calibrating 1st DAC')
			self.rotationalPower(50)
			should_be = 0.5*3.42
			actual = raw_input("Should be " + str(should_be) + " V, what do you see? ")
			self.multiplierLock.acquire()
			self.rotationalMultiplier = self.rotationalMultiplier*float(should_be)/float(actual)
			self.multiplierLock.release()
			self.rotationalPower(50)
			check = raw_input("Does that look good? 1=yes, 0=no: ")
			if check == '1' or check == "1":
				break
			print('\n')
		while True:
			print('Calibrating 2nd DAC')
			self.lateralPower(50)
			should_be = 0.5*3.42
			actual = raw_input("Should be " + str(should_be) + " V, what do you see? ")
			self.multiplierLock.acquire()
			self.lateralMultiplier = self.lateralMultiplier*(float(should_be)/float(actual))
			self.multiplierLock.release()
			self.lateralPower(50)
			check = raw_input("Does that look good? 1=yes, 0=no: ")
			if check == '1' or check == "1":
				break
			print('\n')
		while True:
			print('Calibrating 3rd DAC')
			self.forwardPower(50)
			should_be = 0.5*3.42
			actual = raw_input("Should be " + str(should_be) + " V, what do you see? ")
			self.multiplierLock.acquire()
			self.forwardMultiplier = self.forwardMultiplier*float(should_be)/float(actual)
			self.multiplierLock.release()
			self.forwardPower(50)
			check = raw_input("Does that look good? 1=yes, 0=no: ")
			if check == '1' or check == "1":
				break
			print('\n')
		with open('multipliers.txt', 'w+') as outfile:
			outfile.write(str(self.verticalMultiplier)+'\n')
			outfile.write(str(self.rotationalMultiplier)+'\n')
			outfile.write(str(self.lateralMultiplier)+'\n')
			outfile.write(str(self.forwardMultiplier)+'\n')
			
	

	def test1(self,power,time_):
		self.verticalPower2(power)
		time.sleep(time_)
		self.verticalPower2(52)

		time.sleep(4)
		for i in range(0,50):
			self.verticalPower2(50-i-1)
			time.sleep(0.2)
	
	def verticalPower2(self, power):
		diff = power - self.currVerticalPower
		currPower = self.currVerticalPower
		third = 1
		if diff < 0:
			third = -1
		for i in range(0, diff+third, third):
			self.verticalPower(currPower+i)
			print(self.currVerticalPower)


	def rotationalPower2(self, power):
		diff = power - self.currRotationalPower
		currPower = self.currRotationalPower
		third = 1
		if diff < 0:
			third = -1
		for i in range(0, diff+third, third):
			self.rotationalPower(currPower+i)
			print(self.currRotationalPower)
	def  lateralPower2(self, power):
		diff = power - self.currLateralPower
		currPower = self.currLateralPower
		third = 1
		if diff < 0:
			third = -1
		for i in range(0, diff+third, third):
			self.lateralPower(currPower+i)
			print(self.currLateralPower)
	def forwardPower2(self, power):
		diff = power - self.currForwardPower
		currPower = self.currForwardPower
		third = 1
		if diff < 0:
			third = -1
		for i in range(0, diff+third, third):
			self.forwardPower(currPower+i)
			print(self.currForwardPower)

	


	def lisener(self):
		ser = serial.Serial('dev/tty.usbserial', 9600)
		while(True):
			voltages = ser.readLine().split(" ")
			errVertical = (round(float(voltages[0],2)) == round(float(self.currVerticalVoltage),2))
			errRotational = (round(float(voltages[1],2)) == round(float(self.currRotationalVoltage),2))
			errLateral = (round(float(voltages[2],2))== round(float(self.currLateralVoltage),2))
			errForward = (round(float(voltages[3],2)) == round(float(self.currForwardVoltage),2))
			if errVertical :
				self.verticalMultiplier = self.verticalMultiplier*float(self.currVerticalVoltage)/float(voltages[0])
				self.verticalPower(self.currVerticalPower)
	                if errRotational :
        	                self.rotationalMultiplier = self.rotationalMultiplier*float(self.currRotationalVoltage)/float(voltages[1])
                	        self.rotationalPower(self.currRotationalPower)
			if errLateral :
				self.lateralMultiplier = self.lateralMultiplier*float(self.currLateralMultiplier)/float(voltages[2])
				self.lateralPower(self.currLateralPower)
			if errForwarrd:
				seld.forwardMultiplier = self.forwardMultiplier*float(self.currForwardMultiplier)/float(voltages[3])
				self.forwardPower(self.currForwardPower)





g = controller(5.0)
g.setLiftOffPowerLevels()
threadingg.Thread(target=g.listener).start()
