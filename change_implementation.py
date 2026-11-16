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
                t0=ticks_ms()
                while ticks_diff(ticks_ms(), t0)<300: #how long to pass junction
                    steer, lastError = direction_control.straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
                motorR.off()
                motorL.off()
                proceed = 0
                print("Going straight")
            elif route[x]==1: #turn left before dropoff
                steer, lastError = direction_control.turn90(route[x],"Left", 990, motorR, motorL, BASESPEED, lineSensML, lineSensMR, MAXSTEER, steer, lastError, STEP)
                t0=ticks_ms()
                while ticks_diff(ticks_ms(), t0)<500:
                    steer, lastError = direction_control.straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
                motorR.off()
                motorL.off()
                proceed = 1
                print("Turning left")
            elif route[x]==1.5: #turn left
                steer, lastError = direction_control.turn90(route[x],"Left", 1200, motorR, motorL, BASESPEED, lineSensML, lineSensMR, MAXSTEER, steer, lastError, STEP)
                t0=ticks_ms()
                while ticks_diff(ticks_ms(), t0)<300:
                    steer, lastError = direction_control.straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
                motorR.off()
                motorL.off()
                proceed = 0
                print("Turning left")
            elif route[x]==1.7: #turn last left
                steer, lastError = direction_control.turn90(route[x],"Left", 1200, motorR, motorL, BASESPEED, lineSensML, lineSensMR, MAXSTEER, steer, lastError, STEP)
                t0=ticks_ms()
                while ticks_diff(ticks_ms(), t0)<300:
                    steer, lastError = direction_control.straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
                motorR.off()
                motorL.off()
                proceed = 0
                print("Turning left")
            elif route[x]==2: #turn right before pickup
                steer, lastError = direction_control.turn90(route[x],"Right", 1100, motorR, motorL, BASESPEED, lineSensML, lineSensMR, MAXSTEER, steer, lastError, STEP)
                t0=ticks_ms()
                while ticks_diff(ticks_ms(), t0)<2000:
                    steer, lastError = direction_control.straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
                motorR.off()
                motorL.off()
                proceed = 1
                print("Turning right")
            elif route[x]==2.5: #turn right default
                steer, lastError = direction_control.turn90(route[x],"Right", 1100, motorR, motorL, BASESPEED, lineSensML, lineSensMR, MAXSTEER, steer, lastError, STEP)
                t0=ticks_ms()
                while ticks_diff(ticks_ms(), t0)<500:
                    steer, lastError = direction_control.straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
                motorR.off()
                motorL.off()
                print("Turning right")
                proceed = 0
            elif route[x]== 3: #pause to pick up then proceed
                t0=ticks_ms()
                while (ticks_ms()-t0)<3000:
                    motorR.off()
                    motorL.off()
                proceed = 1
                print("Picking up")
            elif route[x]== 5: #pause to drop then proceed
                t0=ticks_ms()
                while (ticks_ms()-t0)<2000:
                    motorR.off()
                    motorL.off()
                proceed = 1 #or 0?
                print("Dropping")
            elif route[x]== 6: #turn 180 after pickup
                steer, lastError = direction_control.turn180("Left", 2300, motorR, motorL, BASESPEED, lineSensML, lineSensMR, MAXSTEER, steer, lastError, STEP)
                t0=ticks_ms()
                while ticks_diff(ticks_ms(), t0)<1000:
                    steer, lastError = direction_control.straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
                motorR.off()
                motorL.off()
                proceed = 0
                print("Turning 180")
            elif route[x]== 6.5: #turn 180 after dropoff
                t0=ticks_ms()
                while ticks_diff(ticks_ms(), t0)<1000:
                    steer, lastError = direction_control.straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
                steer, lastError = direction_control.turn180("Left", 2300, motorR, motorL, BASESPEED, lineSensML, lineSensMR, MAXSTEER, steer, lastError, STEP)
                t0=ticks_ms()
                while ticks_diff(ticks_ms(), t0)<500:
                    steer, lastError = direction_control.straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
                proceed = 0
                print("Turning 180")
            x+=1
        else: #no change detected, line following protocol
            steer, lastError = direction_control.straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
    motorR.off()
    motorL.off()
    #sleep(0.05)
            
        
        
