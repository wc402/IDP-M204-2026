from machine import PIN
from time import ticks_ms, ticks_diff
from motor_test import Motor
from direction_control import straight
from direction_control import turn90

## Initialise variables
BASESPEED=50 #when driving straight, %
STEP =2 #steering added per loop whilst off centre
MAXSTEER=30 # maximum steering amount
steer=0 #current steering amount
lastError =0 #error value to use if line lost
TIMEOUT=5000 # turn time limit (milliseconds)
# Get sensor readings
lineSensML=Pin(19, Pin.IN, Pin.PULL_DOWN) #Change these pins to suit the actual wiring
lineSensMR=Pin(20, Pin.IN, Pin.PULL_DOWN)

## Route for line following test
toBay=[1,0,2,0,0,0,2,3,4,2,0,0,1,0,5,4,2,1,0]


