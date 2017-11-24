import time

# Import the MCP4725 module.
import Adafruit_MCP4725

from wiringSetup import *


dac = Adafruit_MCP4725.MCP4725()

select_pin = [7,11,13,15]

def setUp():
	initPins()
	setup(select_pin, [])
def enable(p):
	if p < 0 or p > 3:
		print('invalid')
		return
	if p == 0:
		turnOff(select_pin[0])
		turnOn(select_pin[1])
		turnOn(select_pin[2])
		turnOn(select_pin[3])
	elif p == 1:
		turnOn(select_pin[0])
		turnOff(select_pin[1])
		turnOn(select_pin[2])
		turnOn(select_pin[3])
	elif p == 2:
		turnOn(select_pin[0])
		turnOn(select_pin[1])
		turnOff(select_pin[2])
		turnOn(select_pin[3])
	elif p == 3:
		turnOn(select_pin[0])
		turnOn(select_pin[1])
		turnOn(select_pin[2])
		turnOff(select_pin[3])
# assume out of 5 V
def setVoltage(val):
	lvl = ((val/5.0)*4096)
	dac.set_voltage(lvl)
