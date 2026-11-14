from motor_test import Motor
from change_implementation_new import follow_route
from machine import Pin
#from direction_control import getLineSens

## Initialise variables
MAXSTEER=20 # maximum steering amount
BASESPEED=70 #when driving straight, %
TIMEOUT=990 #turn time limit (milliseconds)
TIMEOUT_PICK=960 #time to reach pickup bay (milliseconds)
TIMEOUT_DROP=500 #time to reach dropoff area (milliseconds)
steer=0 #current steering amount
lastError =0 #error value to use if line lost
STEP =1 #weight given to error, bigger value = stronger correction
    
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
#toBay=[0,4,0,0,5,7,8,1,3,9,10,1,0,1,0]
test=[0,0,0,0,2]
#MAKE SURE TO NOT START ON A JUNCTION
follow_route(test, lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT, TIMEOUT_PICK, TIMEOUT_DROP, steer, lastError, STEP)

#Number assignment (integers to avoid bugs)
#0: straight ahead
#1: left turn, default
#2: left turn, pickup (distance sensor)
#3: left turn, dropoff (colour sensor)
#4: right turn, default
#5: right turn, pickup (distance sensor)
#6: right turn, dropoff (colour sensor)
#7: pickup (follows 2 or 5)
#8: 180 after pickup (follows 7)
#9: dropoff
#10: return (same as 180 but doesn't need forced, since it reaches t-junction)