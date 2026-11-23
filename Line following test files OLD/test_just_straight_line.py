#code to test just straight line following

from motor_test import Motor
from change_implementation import follow_route
from machine import Pin
from direction_control import straight

## Initialise variables
MAXSTEER=30 # maximum steering amount
BASESPEED=70 #when driving straight, %
TIMEOUT=5000 # turn time limit (milliseconds)
steer=0 #current steering amount
lastError =0 #error value to use if line lost
STEP =5 #steering added per loop whilst off centre
    
# Get sensor readings
lineSensFL=Pin(28, Pin.IN, Pin.PULL_DOWN)
lineSensML=Pin(27, Pin.IN, Pin.PULL_DOWN) #Change these pins to suit the actual wiring
lineSensMR=Pin(26, Pin.IN, Pin.PULL_DOWN)
lineSensFR=Pin(22, Pin.IN, Pin.PULL_DOWN)

##Connect to motors
motorR=Motor(dirPin=4, PWMPin=5) #Connects to right wheel
motorL=Motor(dirPin=7, PWMPin=6) #Connects to left wheel (dir/pwm swapped here)

route=[0,0,0,0,0,0]
length = len(route)
x=0
for i in range(length): #iterate through each change in route
    steer, lastError = direction_control.straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)

