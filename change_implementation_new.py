from change_detection import make_change
import direction_control
from time import sleep, ticks_ms, ticks_diff


#e.g. route = left_bay
def follow_route(route, lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT, TIMEOUT_PICK, TIMEOUT_DROP, steer, lastError, STEP):
    
    length = len(route)
    x=0
    
    while x<length:
        act = make_change(route[x], lineSensFL, lineSensFR) #final decision on whether to make a change
        if act == True:
            if route[x] == 0: #straight ahead
                #straight line protocol
                steer, lastError = direction_control.straight(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, steer, lastError, STEP)
                print('Straight ahead')
            elif route[x] == 1: #left turn, default
                #turn90
                steer, lastError = direction_control.turn90('Left', lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT, steer, lastError, STEP)
                print('Left')
            elif route[x] == 2: #left turn, pickup
                #turn 90
                steer, lastError = direction_control.turn90('Left', lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT, steer, lastError, STEP)
                print('Left')
                #proceed straight line for time_pick
                print('Continue till pickup bay')
                steer, lastError = direction_control.keep_going(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT_PICK, steer, lastError, STEP)
            elif route[x] == 3: #left turn, dropoff
                #turn 90
                steer, lastError = direction_control.turn90('Left', lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT, steer, lastError, STEP)
                print('Left')
                #proceed straight line for time_drop
                print('Continue till dropoff area')
                steer, lastError = direction_control.keep_going(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT_DROP, steer, lastError, STEP)
            elif route[x] == 4: #right turn, default
                #turn 90
                steer, lastError = direction_control.turn90('Right', lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT, steer, lastError, STEP)
                print('Right')
            elif route[x] == 5: #right turn, pickup
                #turn 90
                steer, lastError = direction_control.turn90('Right', lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT, steer, lastError, STEP)
                print('Right')
                #proceed straight line for time_pick
                print('Continue till pickup bay')
                steer, lastError = direction_control.keep_going(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT_PICK, steer, lastError, STEP)
            elif route[x] == 6: #right turn, dropoff
                #turn 90
                steer, lastError = direction_control.turn90('Right', lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT, steer, lastError, STEP)
                print('Right')
                #proceed straight line for time_drop
                print('Continue till dropoff area')
                steer, lastError = direction_control.keep_going(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT_DROP, steer, lastError, STEP)
            elif route[x] == 7: #pickup (forced change)
                #stop motors for 3 seconds
                motorR.off()
                motorL.off()
                print('Pickup')
                sleep(3)
            elif route[x] == 8: #turn180 (forced change)
                #turn 180 by applying turn 90 for 2*TIMEOUT
                steer, lastError = direction_control.turn90('Left', lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, 2*TIMEOUT, steer, lastError, STEP)
                print('Spin 180')
            elif route[x] == 9: #dropoff
                #stop motors for 3 seconds
                motorR.off()
                motorL.off()
                print('Dropoff')
                sleep(3)
            elif route[x] == 10: #return (turn180 after end t-junction)
                #turn 180 by applying turn 90 for 2*TIMEOUT
                steer, lastError = direction_control.turn90('Left', lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, 2*TIMEOUT, steer, lastError, STEP)
                print('Spin 180')
            else:
                print('Invalid route number?? ', route[x])
                
            x+=1 #move onto next change
            #centre to line again before moving on (might cause problems for pickup->turn 180)
            #steer, lastError = direction_control.straight(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, steer, lastError, STEP)
        else:
            #straight line protocol
            steer, lastError = direction_control.straight(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, steer, lastError, STEP)
    
    #finished route
    motorR.off()
    motorL.off()