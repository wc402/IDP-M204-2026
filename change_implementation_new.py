from change_detection import make_change, is_clear_detected
import direction_control
from time import sleep, ticks_ms, ticks_diff
import grabber_program


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
            elif route[x] == 3: #left turn, dropoff
                print('Left')
                steer, lastError = direction_control.turn('Left', lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL, MAXSTEER, BASESPEED, SEARCH_SPEED, TIMEOUT, steer, lastError, STEP)
                #proceed straight line for time_drop
                print('Continue till dropoff area')
                steer, lastError = direction_control.keep_going(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT[4], steer, lastError, STEP)
            elif route[x] == 4: #right turn, default
                steer, lastError = direction_control.turn('Right', lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL, MAXSTEER, BASESPEED, SEARCH_SPEED, TIMEOUT, steer, lastError, STEP)
                print('Right')
            elif route[x] == 5: #right turn, pickup
                steer, lastError = direction_control.turn('Right', lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL, MAXSTEER, BASESPEED, SEARCH_SPEED, TIMEOUT, steer, lastError, STEP)
                print('Right')
            elif route[x] == 6: #right turn, dropoff
                steer, lastError = direction_control.turn('Right', lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL, MAXSTEER, BASESPEED, SEARCH_SPEED, TIMEOUT, steer, lastError, STEP)
                print('Right')
                #proceed straight line for time_drop
                print('Continue till dropoff area')
                steer, lastError = direction_control.keep_going(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, TIMEOUT[4], steer, lastError, STEP)
            elif route[x] == 7: #pickup (forced change)
                steer, lastError = direction_control.straight(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, steer, lastError, STEP)
                print('Pickup')
                t0=ticks_ms()
                while ticks_diff(ticks_ms(), t0)<TIMEOUT[3]: #TIMEOUT[3] is time to reach pickup bay w/o detections
                    #distance = tof.read()
                    #print("Distance:", distance, "mm")
                    #if distance is None or distance <= 0:
                    #    print("Invalid reading - continuing")
                    #elif distance <= 500: #calibrate 500 to distance required for pickup
                    #    print("Package detected!")
                    #    motorR.off()
                    #    motorL.off()
                    #    grabber_program.close_grabber(CLOSED_ANGLE)
                    #    break
                    #steer, lastError = direction_control.straight(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, steer, lastError, STEP)
                    
                    #TIMER METHOD UNTIL TOF FIXED
                    steer, lastError = direction_control.straight(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, steer, lastError, STEP)
                motorR.off()
                motorL.off()
                grabber_program.close_grabber()
            elif route[x] == 8: #dropoff
                print('Dropoff')
                motorR.off()
                motorL.off()
                grabber_program.open_grabber()
            elif route[x] == 9: #turn180 (forced change)
                steer, lastError = direction_control.turn180('Left', lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL, MAXSTEER, BASESPEED, SEARCH_SPEED, TIMEOUT, steer, lastError, STEP)
                print('Spin 180')
            elif route[x] == 10: #return (turn180 after end t-junction)
                steer, lastError = direction_control.turn180('Left', lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL, MAXSTEER, BASESPEED, SEARCH_SPEED, TIMEOUT, steer, lastError, STEP)
                print('Spin 180')
            elif route[x] == 11: #reverse
                print('Reverse')
                while lineSensFL.value() != 1 or lineSensFR.value() != 1:
                    steer, lastError = direction_control.reverse(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, steer, lastError, STEP)
            else:
                print('Invalid route number?? ', route[x])
            
            #if route[x] not in [7,8,9,10]:
                #will continue last motor settings until junction is cleared
                #is_clear_detected(lineSensFL, lineSensFR)
            #if route[x] is in [7,8,9,10] then don't want to need junction cleared to continue
            x+=1
            
        else:
            #straight line protocol
            steer, lastError = direction_control.straight(lineSensML, lineSensMR, motorR, motorL, MAXSTEER, BASESPEED, steer, lastError, STEP)
    
    #finished route
    motorR.off()
    motorL.off()
