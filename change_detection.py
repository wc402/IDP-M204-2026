from utime import sleep_ms

def is_change_detected(lineSensFL, lineSensML, lineSensMR, lineSensFR, motorR, motorL):
    no_checks = 5 #how many verification checks before commit to a move
    majority = 0
    #verify that a change is happening
<<<<<<< HEAD
    while count != no_checks:
        #lineSensFL, lineSensML, lineSensMR, lineSensFR = getLineSens("True")
=======
    for i in range(no_checks):
        lineSensFL, lineSensML, lineSensMR, lineSensFR = getLineSens("True")
>>>>>>> e4f2c9c11486831e54bbc0dcc5490108e1c9fd6f
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
