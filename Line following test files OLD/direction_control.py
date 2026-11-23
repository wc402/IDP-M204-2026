from time import ticks_ms, ticks_diff, sleep

def straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP):
    error= lineSensML.value()-lineSensMR.value()
    if error !=0: #Robot off centre but still detecting line (only one sensor on). Correction grows with each step
        lastError=error
        steer-=error*STEP
    elif lineSensML.value()==0 and lineSensMR.value()==0: #Line lost (both sensors off)
        steer+=lastError*STEP #Keep turn in the opposite direction as when a line last detected
    else: #Following line correctly, do nothing
        steer = 0 
    steer=max(-MAXSTEER, min(MAXSTEER, steer))
    motorR.Forward(BASESPEED-steer)
    motorL.Forward(BASESPEED+steer)
    return steer, lastError


def turn90(current_move, direction, TIMEOUT, motorR, motorL, BASESPEED, lineSensML, lineSensMR, MAXSTEER, steer, lastError, STEP):
    if current_move == 1.5 or current_move == 1.7 or current_move == 2.5:
        t0=ticks_ms()
        while ticks_diff(ticks_ms(), t0)<800:
            motorR.Forward(BASESPEED)
            motorL.Forward(BASESPEED)
    elif current_move == 1:
        t0=ticks_ms()
        while ticks_diff(ticks_ms(), t0)<500:
            steer,lastError = straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
    else:
        t0=ticks_ms()
        while ticks_diff(ticks_ms(), t0)<800:
            steer,lastError = straight(lineSensML, lineSensMR, MAXSTEER, motorR, motorL, BASESPEED, steer, lastError, STEP)
    if direction=="Left":
        motorR.Forward(BASESPEED)
        motorL.Reverse(BASESPEED)
    else:
        motorR.Reverse(BASESPEED)
        motorL.Forward(BASESPEED)

    t0=ticks_ms()
    while ticks_diff(ticks_ms(), t0)<TIMEOUT:
        pass
    return 0,0

def turn180(direction, TIMEOUT, motorR, motorL, BASESPEED, lineSensML, lineSensMR, MAXSTEER, steer, lastError, STEP):
    if direction=="Left":
        motorR.Forward(BASESPEED)
        motorL.Reverse(BASESPEED)
    else:
        motorR.Reverse(BASESPEED)
        motorL.Forward(BASESPEED)

    t0=ticks_ms()
    while ticks_diff(ticks_ms(), t0)<TIMEOUT:
        pass
    return 0,0
    



