from time import ticks_ms, ticks_diff, sleep
from machine import Pin
from motor_test import Motor

def getLineSens(getOuter):
    lineSensFL=Pin(28, Pin.IN, Pin.PULL_DOWN)
    lineSensML=Pin(27, Pin.IN, Pin.PULL_DOWN) #Change these pins to suit the actual wiring
    lineSensMR=Pin(26, Pin.IN, Pin.PULL_DOWN)
    lineSensFR=Pin(22, Pin.IN, Pin.PULL_DOWN)
    if getOuter:
        return (lineSensFL, lineSensML, lineSensMR, lineSensFR)
    else:
        return (lineSensML, lineSensMR)

def straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP):
    error= lineSensML.value()-lineSensMR.value()
    if error !=0: #Robot off centre but still detecting line. Correction grows with each step
        lastError=error
        steer+=error*STEP
    elif lineSensML.value()==0 and lineSensMR.value()==0: #Line lost 
        steer+=lastError*STEP #Keep turning the same direction as when a line last detected
    else: #Following line correctly, do nothing
        steer = 0 
    steer=max(-MAXSTEER, min(MAXSTEER, steer))
    motorR.Forward(BASESPEED+steer)
    motorL.Forward(BASESPEED-steer)
    print(lineSensML.value(), lineSensMR.value(), steer)
    return steer, lastError
def turn90(direction, TIMEOUT, motorR, motorL, BASESPEED, lineSensML, lineSensMR, MAXSTEER, steer, lastError, STEP):
    straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
    sleep(0.5) #Delay set to move wheels onto junction
    if direction=="Left":
        motorR.Forward(BASESPEED)
        motorL.Reverse(BASESPEED)
    else:
        motorR.Reverse(BASESPEED)
        motorL.Forward(BASESPEED)

    t0=ticks_ms()
    while lineSensML.value()==1 or lineSensMR.value()==1:
        if ticks_diff(ticks_ms(), t0)>TIMEOUT:
            motorL.off()
            break
        lineSensML, lineSensMR= getLineSens(False)
    while not(lineSensML.value()==1 and lineSensMR.value()==1):
        if ticks_diff(ticks_ms(), t0)>TIMEOUT:
            motorR.off()
            break
        lineSensML, lineSensMR= getLineSens(False)
    return 0,0
def reverse(motorR, motorL, BASESPEED):
    motorR.Reverse(BASESPEED)
    motorL.Reverse(BASESPEED)
    sleep(1) # Allow robot to reverse off junction
    lineSensFL, lineSensML, lineSensMR, lineSensFR = getLineSens(True)
    while (lineSensFL.value()==0 or lineSensFR.value()==0):
        lineSensFL, lineSensML, lineSensMR, lineSensFR = getLineSens(True)
        pass
