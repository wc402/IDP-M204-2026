from time import ticks_ms, ticks_diff, sleep


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


def turn(direction, lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL, MAXSTEER, BASESPEED, SEARCH_SPEED, time, steer, lastError, STEP):
    #firstly, move wheels onto junction
    steer, lastError = keep_going(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, 1, steer, lastError, STEP)
    
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
        sleep(0.001) #just to let processor rest
    
    #adjust back onto straight line after turn
    steer, lastError = 0,0
    line_lost(direction, lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL, SEARCH_SPEED)
    steer, lastError = straight(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, steer, lastError, STEP)
    return steer, lastError


def keep_going(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, time, steer, lastError, STEP):
    #before turning, keep going in a straight line for 1 second to move wheels onto junction
    #or
    #after turning, keep going in a straight line for TIMEOUT_PICK/DROP milliseconds
    t0=ticks_ms()
    while ticks_diff(ticks_ms(), t0)<time:
        steer, lastError = straight(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, steer, lastError, STEP)
    motorR.off()
    motorL.off()
    #theoretically, any change that calls keep_going is followed by a pause so this shouldn't matter, but just in case
    return steer, lastError


def line_lost(direction, lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL, SEARCH_SPEED):
    if direction == 'Right':
        if lineSensFR.value()==1: #not turned enough
            while lineSensMR.value()==0: #turn right until get middle sensor back on line
                motorR.Reverse(SEARCH_SPEED)
                motorL.Forward(SEARCH_SPEED)
        elif lineSensFL.value()==1: #turned too much
            while lineSensML.value()==0: #turn left until get middle sensor back on line
                motorR.Forward(SEARCH_SPEED)
                motorL.Reverse(SEARCH_SPEED)
    elif direction == 'Left':
        if lineSensFL.value()==1: #not turned enough
            while lineSensML.value()==0: #turn left until get middle sensor back on line
                motorL.Reverse(SEARCH_SPEED)
                motorR.Forward(SEARCH_SPEED)
        elif lineSensFR.value()==1: #turned too much
            while lineSensMR.value()==0: #turn right until get middle sensor back on line
                motorL.Forward(SEARCH_SPEED)
                motorR.Reverse(SEARCH_SPEED)
    #problem: if ML or MR never lights up, will be stuck in infinite loop
    #problem: if both FL and FR are on, only executes first of if else statement
    #problem: if both F and M sensors are on, what happens?
    
    
    
    
    