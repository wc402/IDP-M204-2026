from change_detection import make_change
import direction_control
from time import sleep, ticks_ms, ticks_diff


#e.g. route = left_bay
def follow_route(route, lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT, TIMEOUT_PICK, TIMEOUT_DROP, steer, lastError, STEP):
    
    length = len(route)
    x=0
    act = False #final decision on whether to make a change
    already_changing = False #signals whether a change is currently being made
    
    while x<length:
        act = make_change(lineSensFL, lineSensFR, route[x], already_changing)
        if act == True:
            if route[x] == 0: #straight ahead
                #straight line protocol
                steer, lastError = direction_control.straight(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, steer, lastError, STEP)
            elif route[x] == 1: #left turn, default
                #turn90
                steer, lastError = direction_control.turn90('Left', lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT, steer, lastError, STEP)
            elif route[x] == 2: #left turn, pickup
                #turn 90
                steer, lastError = direction_control.turn90('Left', lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT_PICK, steer, lastError, STEP)
                #proceed straight line for time_pick
            elif route[x] == 3: #left turn, dropoff
                #turn 90
                steer, lastError = direction_control.turn90('Left', lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT_DROP, steer, lastError, STEP)
                #proceed straight line for time_drop
            elif route[x] == 4: #right turn, default
                #turn 90
                steer, lastError = direction_control.turn90('Right', lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT, steer, lastError, STEP)
            elif route[x] == 5: #right turn, pickup
                #turn 90
                steer, lastError = direction_control.turn90('Right', lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT_PICK, steer, lastError, STEP)
                #proceed straight line for time_pick
            elif route[x] == 6: #right turn, dropoff
                #turn 90
                steer, lastError = direction_control.turn90('Right', lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT_DROP, steer, lastError, STEP)
                ##proceed straight line for time_drop
            elif route[x] == 7: #pickup (follows 2 or 5)
                #stop motors for 3 seconds
            elif route[x] == 8: #turn180 (follows 7)
                #turn 180
            elif route[x] == 9: #dropoff
                #stop motors for 3 seconds
                motorR.off()
                motorL.off()
                sleep(3)
            elif route[x] == 10: #return (turn180 after end t-junction)
                #turn 180
                
            x+=1 #move onto next change
        else:
            #straight line protocol
            steer, lastError = direction_control.straight(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, steer, lastError, STEP)
    
    #finished route
    motorR.off()
    motorL.off()