from utime import sleep_ms

def is_change_detected(lineSensFL, lineSensFR):
    no_checks = 5 #how many verification checks before commit to a move
    majority = 0
    #verify that a change is happening
    for i in range(no_checks):
        if (lineSensFL.value()==1 or lineSensFR.value()==1): #change detected, outside sensor on
            majority += 1
        #pause to verify change
        sleep_ms(1)
        
    return majority > 2
  
  

def is_change_forced(current_move):
    if current_move == 3 or current_move == 5: #the actions which require a forced change
        return True
    else:
        return False
  
  
  
def make_change(lineSensFL, lineSensFR, current_move, already_changing):
    if already_changing == False: #not currently making a change
        
        detect_change = is_change_detected(lineSensFL, lineSensFR)
        force_change = is_change_forced(current_move)
        
        if detect_change == True or force_change == True:
            return True
        else:
            return False
    else: #currently implementing a change, ignore other outer sensor readings
        return False
