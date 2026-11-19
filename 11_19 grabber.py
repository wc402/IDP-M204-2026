from machine import Pin, PWM, ADC
from time import sleep, ticks_ms, ticks_diff

servo = PWM(Pin(15))
servo.freq(50)
feedback = ADC(Pin(26))

#need to calibrate to grabber
MIN_ANGLE = 0
MAX_ANGLE = 180

OPEN_ANGLE = 0 #grabber arms wide open
TARGET_ANGLE = 90 #angle for which expect box to be
EXTRA_ANGLE = 0 #angle to further close for box grab security

#pulse corresponds to servo angle
MIN_PULSE = 500 #microseconds
MAX_PULSE = 2500 #microseconds

#need to calibrate to servo
ADC_MIN = 5000
ADC_MAX = 60000

#need to twiddle
ALLOWABLE_ERROR = 3 #error below which we disregard
ERROR_THRESHOLD = 10 #degrees
DETECTION_TIME = 300 #milliseconds


def set_servo_angle(angle):
    angle = max(MIN_ANGLE, min(MAX_ANGLE, angle)) #keep bounded between min and max angle
    pulse = MIN_PULSE + ((angle - MIN_ANGLE) / (MAX_ANGLE - MIN_ANGLE) * (MAX_PULSE - MIN_PULSE)) #interpolation
    duty = int((pulse / 20000) * 65535) #one pwm cycles lasts 20000, so find fraction
    servo.duty_u16(duty) #function expects number between 0 and 65535
    #sends servo signal for corresponding position


def read_servo_angle():
    total = 0
    for i in range(10):
        total += feedback.read_u16()
        sleep(0.002)
    adc_value = total/10 #average of 10 ADC readings
    #convert ADC reading into angle
    angle = MIN_ANGLE + ((adc_value - ADC_MIN) /(ADC_MAX - ADC_MIN)) * (MAX_ANGLE - MIN_ANGLE) #convert ADC reading into angle value
    #angle = max(MIN_ANGLE, min(MAX_ANGLE, angle)) SURELY shouldn't bound since we want the real life reading
    return angle


def calculate_error(target_angle, actual_angle):
    error = abs(target_angle - actual_angle)

    print("Target angle:", target_angle)
    print("Actual angle:", round(actual_angle, 2))
    print("Position error:", round(error, 2))
    
    return error



def move_and_detect(target_angle):
    set_servo_angle(target_angle)
    obstruction_start = None

    while True:
        actual_angle = read_servo_angle()
        error = calculate_error(target_angle, actual_angle)
        if error > ERROR_THRESHOLD: #if error greater than threshold, we have detected a resistance
            if obstruction_start is None: #timer not started
                obstruction_start = ticks_ms() #start timer
            elif ticks_diff(ticks_ms(), obstruction_start) >= DETECTION_TIME: #if obstruction is detected for long enough
                print("OBSTRUCTION DETECTED!")

                #stop further movement by holding current servo position
                set_servo_angle(actual_angle)
                return True, actual_angle #obstruction detected
        else:
            obstruction_start = None #this makes sure an obstruction has to be detected continuously for DETECTION_TIME

        #movement completed without an obstruction detected
        #POTENTIAL ISSUE: ONE random fluctuation in reading could conclude no obstruction detected
        if error < ALLOWABLE_ERROR:
            return False, actual_angle #no obstruction detected

        sleep(0.02)
        #POTENTIAL ISSUE: infinite loop if error falls between ALLOWABLE_ERROR and ERROR_THRESHOLD


#main program
while True:

    print("Closing grabber")
    obstruction, actual_angle = move_and_detect(TARGET_ANGLE)

    if obstruction:
        print("Box or obstruction detected")
        set_servo_angle(actual_angle+ EXTRA_ANGLE) #if box detected, close a bit more for security
    else:
        print("No obstruction detected")
    sleep(2)

    print("Opening grabber")
    move_and_detect(OPEN_ANGLE) #discard returned value since we only want to move
    sleep(2)
