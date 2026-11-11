from machine import PIN

## Initialise variables
BASESPEED=50 #when driving straight, %
STEP =2 #steering added per loop whilst off centre
MAXSTEER=30 # maximum steering amount
steer=0 #current steering amount
lastError =0 #error value to use if line lost
TIMEOUT=5000 # turn time limit (milliseconds)
# Get sensor readings
mL=Pin(19, Pin.IN, Pin.PULL_DOWN) #Change these pins to suit the actual wiring
mR=Pin(20, Pin.IN, Pin.PULL_DOWN)