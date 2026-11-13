from utime import sleep_ms

def is_change_detected(lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL):
    no_checks = 5 #how many verification checks before commit to a move
    majority = 0
    #verify that a change is happening
    for i in range(no_checks):
        if (lineSensFL.value()==1 or lineSensFR.value()==1): #change detected, outside sensor on
            majority += 1
            #pause to verify change
        sleep_ms(5)
        
    return majority > 2
  
  
  
  
  
  
#elif not(L or R): #at least one of inside sensors are off
#don't do any sensor detections as we do turn protocol
        
    #sleep(.05)
        
#motorR.off()
#motorL.off()

