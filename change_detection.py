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
    if current_move == 7 or current_move == 8: #the actions which require a forced change
        return True
    else:
        return False
  
  
def is_clear_detected(lineSensFL, lineSensFR):
    count = 0
    while count < 5:
        if lineSensFL.value() == 0 and lineSensFR.value() == 0: #no junction detected
            clear_count += 1
        else:
            clear_count = 0
        #pause to verify change
        sleep_ms(1)
    #break out once verify no junction detected 5 times in a row
    #problem: potential infinite loop
    
    
def make_change(current_move, lineSensFL, lineSensFR):
    detect_change = is_change_detected(lineSensFL, lineSensFR)
    force_change = is_change_forced(current_move)
    if detect_change == True or force_change == True:
        return True
    else:
        return False
