import dis
import RPi.GPIO as GPIO
import time

def initPins():
    GPIO.setmode(GPIO.BOARD)

def setup(outputs, inputs):
    for i in inputs:
        GPIO.setup(i, GPIO.IN)
    for o in outputs:
        if o != -1:
            #print(str(o))
            GPIO.setup(o, GPIO.OUT)
    
def turnOn(pin):
    GPIO.output(pin, 1)
    
def turnOff(pin):
    if pin != -1:
        #print(str(pin))
        GPIO.output(pin,0)
    
def delay(amnt):
    time.sleep(amnt)
    
def readPin(pin):
    val = GPIO.input(pin)
    print(str(pin) + " " + str(val))
    return val
#initPins()
#setup([19], [])
