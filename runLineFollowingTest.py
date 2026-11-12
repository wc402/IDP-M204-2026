from time import ticks_ms, ticks_diff, sleep
from motor_test import Motor
from direction_control import straight, turn90, getLineSens
from change_implementation import follow_route

if __name__ == "__main__":
    motorR = Motor(dirPin=4, PWMPin=5)   # right wheel
    motorL = Motor(dirPin=7, PWMPin=6)   # left wheel (dir/pwm swapped on this channel)

## Initialise variables
BASESPEED=70 #when driving straight, %
STEP =5 #steering added per loop whilst off centre
MAXSTEER=30 # maximum steering amount
steer=0 #current steering amount
lastError =0 #error value to use if line lost
TIMEOUT=5000 # turn time limit (milliseconds)
# Get sensor readings
lineSensFL, lineSensML, lineSensMR, lineSensFR=getLineSens(True)
## Connect to motors
#motorR=Motor(dirPin=4, PWMPin=5)
#motorL=Motor(dirPin=7, PWMPin=6)
## Route for line following test
#toBay=[1,0,2,0,0,0,2,3,4,2,0,0,1,5,4,2,1,0]
test=[0,0,0,0,0,0]
follow_route(test, lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT, steer, lastError, STEP)



