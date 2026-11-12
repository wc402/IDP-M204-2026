from change_detection

#e.g. route = left_bay
def follow_route(route):
    length = len(route)
    x=0
    while x != length: #iterate through each change in route
        change = change_detection.is_change_detected() #check if change detected (T/F)
        if change == True:
            i = route[x]
            if i == 0:
                #straight ahead
            elif i == 1:
                #turn left
            elif i == 2:
                #turn right
            elif i == 3:
                #pause to pickup
                #trigger a change detection
            elif i == 4:
                #back up
            elif i == 5:
                #pause to drop
            else:
                #error
            x+=1
            
        
