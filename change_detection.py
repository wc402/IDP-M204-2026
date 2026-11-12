from machine import Pin, PWM
from utime import sleep
from collections import Counter
from motor_test import Motor

#connect pins to sensors/motors
far_left  = Pin(18, Pin.IN, Pin.PULL_DOWN)   # GP18 = header pin 24
left      = Pin(19, Pin.IN, Pin.PULL_DOWN)   # GP19 = header pin 25
right     = Pin(20, Pin.IN, Pin.PULL_DOWN)   # GP20 = header pin 26
far_right = Pin(22, Pin.IN, Pin.PULL_DOWN)   # GP22 = header pin 29

motorR = Motor(dirPin=4, PWMPin=5)   # right wheel
motorL = Motor(dirPin=7, PWMPin=6)   # left wheel (dir/pwm swapped on this channel)
button = Pin(28, Pin.IN, Pin.PULL_DOWN)


def is_change_detected():
    while True:
        no_checks = 5 #how many verification checks before commit to a move
        FL = far_left.value()
        L = left.value()
        R = right.value()
        FR = far_right.value()
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