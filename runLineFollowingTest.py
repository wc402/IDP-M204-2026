from motor_test import Motor
from change_implementation import follow_route
from direction_control import getLineSens
## Initialise variables
BASESPEED=70 #when driving straight, %
STEP =5 #steering added per loop whilst off centre
MAXSTEER=30 # maximum steering amount
steer=0 #current steering amount
lastError =0 #error value to use if line lost
TIMEOUT=5000 # turn time limit (milliseconds)
# Get sensor readings
lineSensFL, lineSensML, lineSensMR, lineSensFR=getLineSens(True)
##Connect to motors
motorR=Motor(dirPin=4, PWMPin=5) #Connects to right wheel
motorL=Motor(dirPin=7, PWMPin=6) #Connects to left wheel (dir/pwm swapped here)
## Route for line following test
#toBay=[1,0,2,0,0,0,2,3,4,2,0,0,1,5,4,2,1,0]
test=[0,0,0,0,0,0]
follow_route(test, lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT, steer, lastError, STEP)



