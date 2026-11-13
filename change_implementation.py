import change_detection
import direction_control
from utime import sleep


#e.g. route = left_bay
def follow_route(route, lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT, steer, lastError, STEP):
    
    length = len(route)
    x=0
    proceed = 0 #used to force a next move after a 3 or 5
    act= True # used to ensure robot doesn't redetect the same junction
    
    while x < length: #iterate through each change in route
        outerSens = lineSensFL.value()==1 or lineSensFR.value()==1
        if not outerSens: #no change detected
            act=True
            
        #only change if no change detected AND change detected
        change = act and change_detection.is_change_detected(lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL) #check if change detected (T/F)
        
        if not change and proceed == 1: #proceed to reverse after pickup/drop off
            change = True
        #Note: should never be the case that change == True and proceed = 1
        if change:
            act=False
            
            match route[x]:
                case 0: #straight ahead
                    steer, lastError = direction_control.straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
                    proceed = 0
                    print("Going straight")
                case 1: #turn left
                    steer, lastError = direction_control.turn90("Left", TIMEOUT, motorR, motorL, BASESPEED, lineSensML, lineSensMR, MAXSTEER, steer, lastError, STEP)
                    proceed = 0
                    print("Turning left")
                case 2: #turn right
                    steer, lastError = direction_control.turn90("Right", TIMEOUT, motorR, motorL, BASESPEED, lineSensML, lineSensMR, MAXSTEER, steer, lastError, STEP)
                    proceed = 0
                    print("Turning right")
                case 3: #pause to pick up then proceed
                    sleep(10)
                    proceed = 1
                    print("Picking up")
                case 4: #backup
                    direction_control.reverse(motorR, motorL, BASESPEED, lineSensFL, lineSensFR)
                    proceed = 0
                    act=True
                    print("Reversing")
                case 5: #pause to drop then proceed
                    sleep(10)
                    proceed = 1
                    print("Dropping")
            x+=1
        else: #no change detected, line following protocol
            steer, lastError = direction_control.straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
    motorR.off()
    motorL.off()
    #sleep(0.05)
            
        

