from motor_test import Motor
from change_implementation_new import follow_route
from machine import Pin
#from direction_control import getLineSens

## Initialise variables
MAXSTEER=20 # maximum steering amount
BASESPEED=70 #when driving straight, %
SEARCH_SPEED=30 #when finding lost line

TIMEOUT_STRAIGHT=300 #time to go straight ahead, passing ONE junction
TIMEOUT_90=980 #turn time limit (milliseconds)
TIMEOUT_180 = 1800 #calibrate separately to TIMEOUT_90 for accuracy
TIMEOUT_PICK=2000 #time to reach pickup bay (milliseconds)
TIMEOUT_DROP=100 #time to reach dropoff area (milliseconds)
TIMEOUT_JUNCTION = 800 #time to get wheels on junction
TIMEOUT_STRAIGHT_AFTER_TURNING=100 #not too long that we miss next junction

steer=0 #current steering amount
lastError =0 #error value to use if line lost
STEP =1 #weight given to error, bigger value = stronger correction
    
# Get sensor readings
lineSensFL=Pin(20, Pin.IN, Pin.PULL_DOWN)
lineSensML=Pin(22, Pin.IN, Pin.PULL_DOWN) #Change these pins to suit the actual wiring
lineSensMR=Pin(26, Pin.IN, Pin.PULL_DOWN)
lineSensFR=Pin(16, Pin.IN, Pin.PULL_DOWN)
#lineSensFL, lineSensML, lineSensMR, lineSensFR=getLineSens(True)

##Connect to motors
motorR=Motor(dirPin=4, PWMPin=5) #Connects to right wheel
motorL=Motor(dirPin=7, PWMPin=6) #Connects to left wheel (dir/pwm swapped here)

#Timeout list
TIMEOUT = [TIMEOUT_STRAIGHT, TIMEOUT_90, TIMEOUT_180, TIMEOUT_PICK, TIMEOUT_DROP, TIMEOUT_JUNCTION, TIMEOUT_STRAIGHT_AFTER_TURNING]
## Route for line following test
test1=[0,0,0] #straight line
test2=[0,4] #first right turn
test3=[0,4,0,0,0]#from start to before pickup
test4=[0,0,0,5]#turn to pickup
test5=[0,0,0,0,0,5,7,9,1,0]#pickup and turn
test6=[0,0,0,0,0,5,7,9,1,0,0,0,0]#pickup and turn and continue
test7=[0,3,8,11,4,1,0,0]#dropoff and return
test8=[0,4,0,0,0,0,0,0,0,5,7,9,1,0,0,0,0,0,3,8,11,4,1,0,1,0,0]#whole route
test9=[0,0,0,0,0,5,7,9,1,0,0,0,0,0,0,0,1,0]#pickup and return
test10=[5,7,9,1,0] #PICKUP TEST (closest bay)
test11 =[3,8,11,4,1] #DROPOFF TEST (closest area)
test12=[7,9]

#DONT LET TIMEOUT_DROP LET JUNCTION BE DETECTED
follow_route(test12, lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL, MAXSTEER, BASESPEED, SEARCH_SPEED, TIMEOUT, steer, lastError, STEP)

#Number assignment (integers to avoid bugs)
#0: straight ahead
#1: left turn, default
#2: left turn, pickup (distance sensor)
#3: left turn, dropoff
#4: right turn, default
#5: right turn, pickup (distance sensor)
#6: right turn, dropoff
#7: pickup (follows 2 or 5)
#8: dropoff
#9: 180 after pickup (follows 7)
#10: return (same as 180 but doesn't need forced, since it reaches t-junction)
#11: reverse