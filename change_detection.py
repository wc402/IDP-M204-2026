from runLineFollowingTest import lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL

def is_change_detected():
    while True:
        no_checks = 5 #how many verification checks before commit to a move
        FL = lineSensFL.value()
        L = lineSensML.value()
        R = lineSensMR.value()
        FR = lineSensFR.value()
        majority = 0
        count = 0
        
        #verify that a change is happening
        while count != check:
            if (FL or FR): #change detected, outside sensor on
                majority += 1
                #pause to verify change
                motorR.off()
                motorL.off()
            count+=1
            
        if majority>2:
            return True #change detected
        else:
            return False #line following protocol
  
  
  
  
  
  
#elif not(L or R): #at least one of inside sensors are off
#don't do any sensor detections as we do turn protocol
        
    #sleep(.05)
        
#motorR.off()
#motorL.off()