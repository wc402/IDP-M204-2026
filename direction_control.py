from time import ticks_ms, ticks_diff

def straight(lineSensML, lineSensMR):
    global steer, lastError
    error= lineSensML-lineSensMR
    if error !=0: #Robot off centre but still detecting line. Correction grows with each step
        lastError=error
        steer+=error*STEP
    elif mL==0 and mR==0: #Line lost 
        steer+=lastError*STEP #Keep turning the same direction as when a line last detected
    else: #Following line correctly, do nothing
        steer = 0 
    steer=max(-MAXSTEER, min(MAXSTEER, steer))
    motorR.Forward(BASESPEED+steer)
    mortorL.Forward(BASESPEED-steer)
    
def turn90(direction, TIMEOUT):
    if direction=="Left":
        motorR.Forward(BASESPEED)
        motorL.Reverse(BASESPEED)
    else:
        motorR.Reverse(BASESPEED)
        motorL.Forward(BASESPEED)
        
    lineSensML, lineSensMR=getLineSens()
    t0=ticks_ms()
    while lineSensML==1 or lineSensMR==1:
        if ticks_diff(ticks_ms(), t0)>TIMEOUT:
            break
        lineSensML, lineSensMR= getLineSens()
    while not(lineSensML=1 and lineSensMR=1):
        if ticks_diff(ticks_ms(), t0)>TIMEOUT:
            break
        lineSensML, lineSensMR= getLineSens()    
def reverse():
    motorR.Reverse(BASESPEED)
    motorL.Reverse(BASESPEED)
    