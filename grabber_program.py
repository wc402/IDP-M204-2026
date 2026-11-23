
from machine import Pin, PWM, ADC
from time import sleep

# ---------------- SERVO SETUP ----------------

servo = PWM(Pin(15))
servo.freq(50)

feedback = ADC(Pin(27))

MIN_ANGLE = 0
MAX_ANGLE = 270

OPEN_ANGLE = 100
CLOSED_ANGLE = 0

MIN_PULSE = 500
MAX_PULSE = 2500

# ---------------- FEEDBACK CALIBRATION ----------------

CAL_TABLE = [
    (0,   5332),
    (27,  11897),
    (54,  18960),
    (81,  26003),
    (108, 32781),
    (135, 39680),
    (162, 46165),
    (189, 51563),
    (216, 56142),
    (243, 60008),
    (270, 62970)
]

# ---------------- SERVO CONTROL ----------------

def set_servo_angle(angle):

    angle = max(MIN_ANGLE, min(MAX_ANGLE, angle))

    pulse = MIN_PULSE + (
        (angle - MIN_ANGLE) / (MAX_ANGLE - MIN_ANGLE)
        * (MAX_PULSE - MIN_PULSE)
    )

    duty = int((pulse / 20000) * 65535)

    servo.duty_u16(duty)


# ---------------- FEEDBACK READING ----------------

def read_adc():

    total = 0

    for i in range(10):
        total += feedback.read_u16()
        sleep(0.002)

    return total / 10


def read_servo_angle():

    adc_value = read_adc()

    for i in range(len(CAL_TABLE) - 1):

        angle0, adc0 = CAL_TABLE[i]
        angle1, adc1 = CAL_TABLE[i + 1]

        if adc0 <= adc_value <= adc1:

            angle = angle0 + (
                (adc_value - adc0) / (adc1 - adc0)
            ) * (angle1 - angle0)

            return angle

    # Extrapolate outside calibration range

    if adc_value < CAL_TABLE[0][1]:
        angle0, adc0 = CAL_TABLE[0]
        angle1, adc1 = CAL_TABLE[1]

    else:
        angle0, adc0 = CAL_TABLE[-2]
        angle1, adc1 = CAL_TABLE[-1]

    return angle0 + (
        (adc_value - adc0) / (adc1 - adc0)
    ) * (angle1 - angle0)


# ---------------- GRABBER FUNCTIONS ----------------

def close_grabber():

    print("Closing grabber - gripping box")

    set_servo_angle(CLOSED_ANGLE)

    sleep(1)

    actual_angle = read_servo_angle()

    print("Grabber angle:", round(actual_angle, 2))


def open_grabber():

    print("Opening grabber - dropping box")

    set_servo_angle(OPEN_ANGLE)

    sleep(1)

    actual_angle = read_servo_angle()

    print("Grabber angle:", round(actual_angle, 2))


# ---------------- MAIN PROGRAM ----------------

#while True:
#    choice = input("grab or drop")
#    if choice == 'grab':
#        close_grabber()
#        sleep(2)
#    elif choice == 'drop':
#        open_grabber()
#        sleep(2)
#    else:
#        print('invalid')