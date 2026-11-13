import change_detection
import direction_control
from time import sleep, ticks_ms, ticks_diff


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
            
            if route[x] ==0: #straight ahead
                steer, lastError = direction_control.straight(lineSensML, lineSensMR, lineSensFR, lineSensFL, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
                steer, lastError = direction_control.straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
                steer, lastError = direction_control.straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
                proceed = 0
                print("Going straight")
            elif route[x]==1: #turn left no pick up
                steer, lastError = direction_control.turn90("Left", TIMEOUT, motorR, motorL, BASESPEED, lineSensML, lineSensMR, MAXSTEER, steer, lastError, STEP)
                steer, lastError = direction_control.straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
                proceed = 0
                print("Turning left")
            elif route[x]==1.5: #turn left pick up
                steer, lastError = direction_control.turn90("Left", TIMEOUT, motorR, motorL, BASESPEED, lineSensML, lineSensMR, MAXSTEER, steer, lastError, STEP)
                steer, lastError = direction_control.straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
                #need distance sensor or colour sensor, or counter depending on turn
                #could separate turn rights into other number cases
                count = 1
                end = False
                while end == False:
                    sleep(0.1) #reduce pause so straight line protocol occurs often 
                    steer, lastError = direction_control.straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
                    count+=1
                    if count == 20:
                        end = True
                proceed = 1
                print("Turning left and picking up")
            elif route[x]==2: #turning right no pick up
                steer, lastError = direction_control.turn90("Right", TIMEOUT, motorR, motorL, BASESPEED, lineSensML, lineSensMR, MAXSTEER, steer, lastError, STEP)
                steer, lastError = direction_control.straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
                proceed = 0                
            elif route[x]==2.5: #turn right pick up
                steer, lastError = direction_control.turn90("Right", TIMEOUT, motorR, motorL, BASESPEED, lineSensML, lineSensMR, MAXSTEER, steer, lastError, STEP)
                steer, lastError = direction_control.straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
                #need distance sensor or colour sensor, or counter depending on turn
                #could separate turn rights into other number cases
                count = 1
                end = False
                while end == False:
                    sleep(0.1) #reduce pause so straight line protocol occurs often 
                    steer, lastError = direction_control.straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
                    count+=1
                    if count == 20:
                        end = True
                proceed = 1
                print("Turning right and picking up")
            elif route[x]== 3: #pause to pick up then proceed
                t0=ticks_ms()
                while (ticks_ms()-t0)<5000:
                    motorR.off()
                    motorL.off()
                proceed = 1
                print("Picking up")
            elif route[x]== 4: #backup
                #direction_control.reverse(motorR, motorL, BASESPEED, lineSensFL, lineSensFR)
                steer, lastError = direction_control.straight_reverse(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
                proceed = 0
                act=True
                print("Reversing")
            elif route[x]== 5: #pause to drop then proceed
                t0=ticks_ms()
                while (ticks_ms()-t0)<5000:
                    motorR.off()
                    motorL.off()
                proceed = 1
                print("Dropping")
            x+=1
        else: #no change detected, line following protocol
            steer, lastError = direction_control.straight(lineSensML, lineSensMR, lineSensFR, lineSensFL, lineSens MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
    motorR.off()
    motorL.off()
    #sleep(0.05)
            
        



