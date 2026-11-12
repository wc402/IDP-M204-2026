import change_detection
import direction_control
from utime import sleep


#e.g. route = left_bay
def follow_route(route):
    length = len(route)
    x=0
    while x != length: #iterate through each change in route
        change = change_detection.is_change_detected() #check if change detected (T/F)
        if change == False and proceed = 1: #proceed to reverse after pickup/drop off
            change == True
        #Note: should never be the case that change == True and proceed = 1
        if change == True:
            i = route[x]
            if i == 0: #straight ahead
                direction_control.straight(lineSensML, lineSensMR)
                proceed = 0
            elif i == 1: #turn left
                direction_control.turn90("Left", TIMEOUT)
                proceed = 0
            elif i == 2: #turn right
                direction_control.turn90("Right", TIMEOUT)
                proceed = 0
            elif i == 3: #pause to pick up then proceed
                sleep(10)
                proceed = 1
            elif i == 4: #backup
                direction_control.reverse()
                proceed = 0
            elif i == 5: #pause to drop then proceed
                sleep(10)
                proceed = 1
            x+=1
        elif change == False:
            direction_control.straight(lineSensML, lineSensMR)
        sleep(0.05)
            
        
