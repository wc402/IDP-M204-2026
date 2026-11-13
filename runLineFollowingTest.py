from motor_test import Motor
from change_implementation import follow_route
from machine import Pin
#from direction_control import getLineSens

## Initialise variables
MAXSTEER=20 # maximum steering amount
BASESPEED=70 #when driving straight, %
TIMEOUT=960 # turn time limit (milliseconds)
steer=0 #current steering amount
lastError =0 #error value to use if line lost
STEP =1 #steering added per loop whilst off centre
    
# Get sensor readings
lineSensFL=Pin(28, Pin.IN, Pin.PULL_DOWN)
lineSensML=Pin(27, Pin.IN, Pin.PULL_DOWN) #Change these pins to suit the actual wiring
lineSensMR=Pin(26, Pin.IN, Pin.PULL_DOWN)
lineSensFR=Pin(22, Pin.IN, Pin.PULL_DOWN)
#lineSensFL, lineSensML, lineSensMR, lineSensFR=getLineSens(True)

##Connect to motors
motorR=Motor(dirPin=4, PWMPin=5) #Connects to right wheel
motorL=Motor(dirPin=7, PWMPin=6) #Connects to left wheel (dir/pwm swapped here)

## Route for line following test
#toBay=[1,0,2,0,0,0,2,3,4,2,0,0,1,5,4,2,1,0]
test=[6]
follow_route(test, lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT, steer, lastError, STEP)



