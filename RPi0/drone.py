


from __future__ import print_function
from dronekit import connect, VehicleMode
import time
import atexit
import dronekit_sitl

class droneStats:

	def __init__(self, connectionString):
		self.connectionString = connectionString

		self.vehicle = connect(connection_string, wait_ready=True, baud=57600)
		self.vehicle.wait_ready('autopilot_version')
		atexit.register(exit_func)
	def getVerticalVelocity(self):
		return self.vehicle.velocity[2]
	def getLateralVelocity(self):
		return self.vehicle.velocity[0]
	def getForwardVelocity(self):
		return self.vehicle.velocity[1]
	def getRotationalPosition():
		return self.vehicle.attitude.yaw
	def armed(self):
		return self.vehicle.armed
	def exit_func(self):
		self.vehicle.close()
