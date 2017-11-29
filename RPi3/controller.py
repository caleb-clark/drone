
import time

# Import the MCP4725 module.
import Adafruit_MCP4725


class controller:


	def __init__(self, dacInputVoltage):
		# Create a DAC instance.
		self.dac = Adafruit_MCP4725.MCP4725() # reference to DAC
		self.dacInputVoltage = dacInputVoltage #input to the DAC 3.3 V or 5 V

		self.RPi0 = pi2pi()

		
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


	def setDefaultPowerLevels(self):
		''' Reset joysticks to their default values '''
		if verticalPower(self.defaultVerticalPower) == -1:
			print ('Idle failed: Could not set vertical power levels')
			return -1
		if rotationalPower(self.defaultRotationalPower) == -1:
			print ('Idle failed: Could not set rotational power levels')
			return -1
		if lateralPower(self.defaultLateralPower) == -1:
			print ('Idle failed: Could not set lateral power levels')
			return -1
		if forwardPower(self.defaultForwardPower) == -1:
			print ('Idle failed: Could not set forward power levels')
			return -1
	def setLiftOffPowerLevels(self):
		''' Reset joysticks to their default values '''
		if verticalPower(0) == -1:
			print ('Lift off failed: Could not set vertical power level for lift off')
			return -1
		if rotationalPower(self.defaultRotationalPower) == -1:
			print ('Lift off failed: Could not set rotational power level for lift off')
			return -1
		if lateralPower(self.defaultLateralPower) == -1:
			print ('Lift off failed: Could not set lateral power level for lift off')
			return -1
		if forwardPower(self.defaultForwardPower) == -1:
			print ('Lift off failed: Could not set forward power level for lift off')
			return -1

	def prepareForLiftOff(self):

		# All drone system checks disabled so we just need to set joysticks to default
		# and check if the drone is armable

		# place the joysticks at appropriate power for liftoff 

		setLiftOffPowerLevels()

		# see if we can arm the drone

		if not self.RPi0.isArmable():
			print('Lift off failed: Drone not armable')
			return -1

		return 0


	def liftOff(self):

		# Need to prepare the drone for liftoff and then slowly
		# ascend until RPi0 tells us to stop. If connection with RPi0 is lost
		# immediately start idling and attempt to reconnect with RPi0

		if self.prepareForLiftOff() == -1:
			print('Lift off failed: Look above for reason')
			return -1

		# Ask the RPi0 if we can arm the drone
		# also notifies the RPi0 that we're arming 
		# and to start checking that it is armed

		print('Requesting permission to arm...')
		if self.RPi0.requestPermissionToArm() == -1:
			print('Could not get permission to arm drone')
			return -1

		print('done.')

		# We have permission and have notified RPi0
		# so now attempt to arm drone

		print('Attempting to arm drone...')

		if self.armDrone() == -1:
			print('Lift off failed: Could not arm drone')
			return -1
		
		print('done')

		# Drone is armed but we have a limited amount of time to increase vertical power
		# before the drone automatically disarms

		# Ramp up vertical power to 50 % quickly since the drone won't take off 
		# until the power is over 50 %

		print('Prepare for lift off!')

		while self.currVerticalPower < 50:
			verticalPower(self.currVerticalPower + 1)
			time.sleep(0.02)

		# anything beyond our current power level will start lifting the drone off
		# the ground. Need more interaction with RPi0 at this point

		ascent_power = RPi0.getLiftOffPower() 

		if ascent_power == -1:
			# if there's not a value set
			# go for something conservative
			ascent_power = 55

		# hope for the best!
		verticalPower(ascent_power)

		if self.RPi0.getStatus() != 0:
			self.badStatusProcedure()
		elif not self.RPi0.connected():
			self.lostConnectionProcedure()

		vertical_power_delta = self.RPi0.getVerticalPowerDelta()


		# 999 means stop moving!
		while vertical_power_delta != 999 and RPi0.getStatus() == 0:
			verticalPower(self.currVerticalPower + vertical_power_delta)
			vertical_power_delta = self.RPi0.getVerticalPowerDelta()

		# We made it!
		verticalPower(self.defaultVerticalPower)

		# Set levels to default to idle

		setDefaultPowerLevels()

	def land():
		''' 
		The land function assumes that the ground is clear but must
		maintain communication with the RPi0 to coordinate landing
		
		'''

		print('Landing procedure initiated, getting permission to land...')

		# hault all movement of the vehicle

		setDefaultPowerLevels()

		while not self.RPi0.clearedForLanding():
			print('Landing was not cleared by RPi0, idling...')
			time.sleep(0.5)

		print('Cleared to land')

		







	def verticalPower(self, power):
		'''
		Set the vertical power of the drone
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
			voltage_dac_val = self.powerToDacVal(power)
			dac.set_voltage(voltage_val)
			self.currVerticalPower = power
			return 0

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
			voltage_dac_val = self.powerToDacVal(power)
			dac.set_voltage(voltage_val)
			self.currRotationalPower = power
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
			voltage_dac_val = self.powerToDacVal(power)
			dac.set_voltage(voltage_val)
			self.currLateralPower = power
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
		elif raw_voltage_val > self.maxVoltage:
			print('Requested value exceeds the joysticks maximum voltage (you might want to switch to 3.3 V input to the DAC)')
			return -1
		else:
			voltage_dac_val = self.powerToDacVal(power)
			dac.set_voltage(voltage_val)
			self.currForwardPower = power
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
		return ((power/100.0) * 4096.0)



