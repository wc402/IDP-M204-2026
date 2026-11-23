
from machine import Pin, PWM
from time import sleep

# ---------------- SCISSOR LIFT SERVO ----------------

lift_servo = PWM(Pin(13))
lift_servo.freq(50)

# Servo angle limits
MIN_ANGLE = 0
MAX_ANGLE = 270

# Change these after testing the lift
UP_ANGLE = 270
DOWN_ANGLE = 0

# Servo pulse range (microseconds)
MIN_PULSE = 500
MAX_PULSE = 2500


# ---------------- SERVO CONTROL ----------------

def set_lift_angle(angle):

    angle = max(MIN_ANGLE, min(MAX_ANGLE, angle))

    pulse = MIN_PULSE + (
        (angle - MIN_ANGLE) / (MAX_ANGLE - MIN_ANGLE)
        * (MAX_PULSE - MIN_PULSE)
    )

    duty = int((pulse / 20000) * 65535)

    lift_servo.duty_u16(duty)


# ---------------- LIFT FUNCTIONS ----------------

def up():

    print("Raising scissor lift")

    set_lift_angle(UP_ANGLE)

    sleep(1)


def down():

    print("Lowering scissor lift")

    set_lift_angle(DOWN_ANGLE)

    sleep(1)


# ---------------- TEST PROGRAM ----------------

while True:
    choice = input('up or down ')
    if choice == 'up':
        up()
        sleep(2)
    if choice == 'down':
        down()
        sleep(2)