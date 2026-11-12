from machine import PIN
from time import ticks_ms, ticks_diff
from motor_test import Motor
from direction_control import straight
from direction_control import turn90
from change_implementation import follow_route
## Initialise variables
BASESPEED=50 #when driving straight, %
STEP =2 #steering added per loop whilst off centre
MAXSTEER=30 # maximum steering amount
steer=0 #current steering amount
lastError =0 #error value to use if line lost
TIMEOUT=5000 # turn time limit (milliseconds)
# Get sensor readings
lineSensFL=Pin(34, Pin.IN, Pin.PULL_DOWN)
lineSensML=Pin(32, Pin.IN, Pin.PULL_DOWN) #Change these pins to suit the actual wiring
lineSensMR=Pin(31, Pin.IN, Pin.PULL_DOWN)
lineSensFR=Pin(29, Pin.IN, Pin.PULL_DOWN)
## Connect to motors
motorR=Motor(dirPin=4, PWMPin=5)
motorL=Motor(dirPin=7, PWMPin=6)
## Route for line following test
toBay=[1,0,2,0,0,0,2,3,4,2,0,0,1,5,4,2,1,0]
follow_route(toBay)


