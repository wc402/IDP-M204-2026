from change_detection import make_change, is_clear_detected
import direction_control
from time import sleep, ticks_ms, ticks_diff


def follow_route(route, lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL, MAXSTEER, BASESPEED, SEARCH_SPEED, TIMEOUT, steer, lastError, STEP):
    
    length = len(route)
    x=0
    
    while x<length:
        act = make_change(route[x], lineSensFL, lineSensFR) #final decision on whether to make a change
        if act == True:
            if route[x] == 0: #straight ahead
                steer, lastError = direction_control.keep_going(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT[0], steer, lastError, STEP)
                print('Straight ahead')
            elif route[x] == 1: #left turn, default
                steer, lastError = direction_control.turn('Left', lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL, MAXSTEER, BASESPEED, SEARCH_SPEED, TIMEOUT, steer, lastError, STEP)
                print('Left')
            elif route[x] == 2: #left turn, pickup
                steer, lastError = direction_control.turn('Left', lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL, MAXSTEER, BASESPEED, SEARCH_SPEED, TIMEOUT, steer, lastError, STEP)
                print('Left')
                #proceed straight line for time_pick
                #print('Continue till pickup bay')
                #t0=0
                #while time_of_flight doesn't pick smt up
                #    if ticks_diff(ticks_ms(), t0)<time:
                #       steer, lastError = straight(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, steer, lastError, STEP)
                #    else: reached pickup zone without detecting
                #        break
                #motorR.off()
                #motorL.off()
                    
            elif route[x] == 3: #left turn, dropoff
                steer, lastError = direction_control.turn('Left', lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL, MAXSTEER, BASESPEED, SEARCH_SPEED, TIMEOUT, steer, lastError, STEP)
                print('Left')
                #proceed straight line for time_drop
                print('Continue till dropoff area')
                steer, lastError = direction_control.keep_going(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT[4], steer, lastError, STEP)
            elif route[x] == 4: #right turn, default
                steer, lastError = direction_control.turn('Right', lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL, MAXSTEER, BASESPEED, SEARCH_SPEED, TIMEOUT, steer, lastError, STEP)
                print('Right')
            elif route[x] == 5: #right turn, pickup
                steer, lastError = direction_control.turn('Right', lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL, MAXSTEER, BASESPEED, SEARCH_SPEED, TIMEOUT, steer, lastError, STEP)
                print('Right')
                #proceed straight line for time_pick
                #print('Continue till pickup bay')
                #t0=0
                #while time_of_flight.value() < distance needed to start pickup:
                #    if ticks_diff(ticks_ms(), t0)<time to get closest to pickup:
                #       steer, lastError = straight(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, steer, lastError, STEP)
                #    else: reached closest to pickup zone without detecting
                #        break
                #motorR.off()
                #motorL.off()
                
            elif route[x] == 6: #right turn, dropoff
                steer, lastError = direction_control.turn('Right', lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL, MAXSTEER, BASESPEED, SEARCH_SPEED, TIMEOUT, steer, lastError, STEP)
                print('Right')
                #proceed straight line for time_drop
                print('Continue till dropoff area')
                steer, lastError = direction_control.keep_going(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT[4], steer, lastError, STEP)
            elif route[x] == 7: #pickup (forced change)
                #hall sensor stuff
                #stop motors for 3 seconds
                motorR.off()
                motorL.off()
                print('Pickup')
                #actual pickup function
                sleep(3)
            elif route[x] == 8: #dropoff
                #stop motors for 3 seconds
                motorR.off()
                motorL.off()
                print('Dropoff')
                #actual dropoff function
                sleep(3)
            elif route[x] == 9: #turn180 (forced change)
                steer, lastError = direction_control.turn180('Left', lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL, MAXSTEER, BASESPEED, SEARCH_SPEED, TIMEOUT, steer, lastError, STEP)
                print('Spin 180')
            elif route[x] == 10: #return (turn180 after end t-junction)
                steer, lastError = direction_control.turn180('Left', lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL, MAXSTEER, BASESPEED, SEARCH_SPEED, TIMEOUT, steer, lastError, STEP)
                print('Spin 180')
            else:
                print('Invalid route number?? ', route[x])
            
            if route[x] not in [7,8,9,10]:
                #will continue last motor settings until junction is cleared
                is_clear_detected(lineSensFL, lineSensFR)
            #if route[x] is in [7,8,9,10] then don't want to need junction cleared to continue
            x+=1 #move onto next change
            
        else:
            #straight line protocol
            steer, lastError = direction_control.straight(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, steer, lastError, STEP)
    
    #finished route
    motorR.off()
    motorL.off()