from time import sleep
from direction_control import getLineSens

def is_change_detected(lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL):
    no_checks = 5 #how many verification checks before commit to a move
    majority = 0
    count = 0
    #verify that a change is happening
    while count != no_checks:
        lineSensFL, lineSensML, lineSensMR, lineSensFR = getLineSens("True")
        if (lineSensFL.value()==1 or lineSensFR.value()==1): #change detected, outside sensor on
            majority += 1
            #pause to verify change
            motorR.off()
            motorL.off()
        count+=1
        
    if majority>2:
        sleep(1)
        return True #change detected
    else:
        sleep(1)
    return False #line following protocol
  
  
  
  
  
  
#elif not(L or R): #at least one of inside sensors are off
#don't do any sensor detections as we do turn protocol
        
    #sleep(.05)
        
#motorR.off()
#motorL.off()
