from time import ticks_ms, ticks_diff, sleep
#from machine import Pin
#from motor_test import Motor

#def getLineSens(getOuter):
#    lineSensFL=Pin(28, Pin.IN, Pin.PULL_DOWN)
#    lineSensML=Pin(27, Pin.IN, Pin.PULL_DOWN) #Change these pins to suit the actual wiring
#    lineSensMR=Pin(26, Pin.IN, Pin.PULL_DOWN)
#    lineSensFR=Pin(22, Pin.IN, Pin.PULL_DOWN)
#    if getOuter:
#        return (lineSensFL, lineSensML, lineSensMR, lineSensFR)
#    else:
#        return (lineSensML, lineSensMR)

def straight(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, steer, lastError, STEP):
    error= lineSensML.value()-lineSensMR.value()
    if error !=0: #Robot off centre but still detecting line (only one sensor on). Correction grows with each step
        lastError=error
        steer-=error*STEP #accumulate steer adjustment
    elif lineSensML.value()==0 and lineSensMR.value()==0: #Line lost (both sensors off)
        steer+=lastError*STEP #Keep turning in the opposite direction as when a line last detected
    else: #Following line correctly, do nothing
        steer = 0
        
    steer=max(-MAXSTEER, min(MAXSTEER, steer)) #limits accumulated steer adjustment between -20 and 20
    
    motorR.Forward(BASESPEED-steer)
    motorL.Forward(BASESPEED+steer)
    return steer, lastError

def turn90(direction, lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, time, steer, lastError, STEP):
    #firstly, move wheels onto junction
    steer, lastError = straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
    sleep(1)
    
    #now, turn
    if direction=="Left":
        motorR.Forward(BASESPEED)
        motorL.Reverse(BASESPEED)
    else:
        motorR.Reverse(BASESPEED)
        motorL.Forward(BASESPEED)
        
    #keep turning till break out of loop
    t0=ticks_ms() #records starting time
    while ticks_diff(ticks_ms(), t0)<time: #finds elapsed time since t0
        pass
    return 0,0 #ideally after turning, sensors are back to middle of line

def turn180(direction, TIMEOUT, motorR, motorL, BASESPEED, lineSensML, lineSensMR, MAXSTEER, steer, lastError, STEP):
    steer, lastError = straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
    sleep(1) #Delay set to move wheels onto junction
    if direction=="Left":
        motorR.Forward(BASESPEED)
        motorL.Reverse(BASESPEED)
    else:
        motorR.Reverse(BASESPEED)
        motorL.Forward(BASESPEED)

    t0=ticks_ms()
    while ticks_diff(ticks_ms(), t0)<2*TIMEOUT:
        pass
    return 0,0
    
def reverse(motorR, motorL, BASESPEED, lineSensFL, lineSensFR, lineSensML, lineSensMR, MAXSTEER, steer, lastError, STEP):
    motorR.Reverse(BASESPEED)
    motorL.Reverse(BASESPEED)
    sleep(3)  # Allow robot to reverse off junction
    while lineSensFL.value() == 0 and lineSensFR.value() == 0:
        steer, lastError = straight_reverse(lineSensML, lineSensMR, MAXSTEER,motorR, motorL, BASESPEED, steer, lastError, STEP)
    motorR.off()
    motorL.off()
    return steer, lastError

def straight_reverse(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP):
    error= lineSensML.value()-lineSensMR.value()
    if error !=0: #Robot off centre but still detecting line (only one sensor on). Correction grows with each step
        lastError=error
        steer+=error*STEP
    elif lineSensML.value()==0 and lineSensMR.value()==0: #Line lost (both sensors off)
        steer+=lastError*STEP #Keep turn in the opposite direction as when a line last detected
    else: #Following line correctly, do nothing
        steer = 0 
    steer=max(-MAXSTEER, min(MAXSTEER, steer))
    motorR.Reverse(BASESPEED+steer)
    motorL.Reverse(BASESPEED-steer)
    print(lineSensML.value(), lineSensMR.value(), steer)
    return steer, lastError


