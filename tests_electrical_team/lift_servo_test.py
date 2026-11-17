# arya_servo_test.py
# Servo test: type an angle (0 to 270) in the Thonny shell and press Enter.
# Type "sweep" to move 0 -> 135 -> 270 -> 135 -> 0.  Stop with Thonny's Stop.
#
# Plug the servo into the PicoBot "Servo 1" port (GP15) - or "Servo 2" (GP13).
# Servo wires: orange = signal, red = power, brown = GND.
# The servo is powered from the battery, so the battery must be on.

from machine import Pin, PWM
from utime import sleep_ms

SERVO_PIN = 15         # 15 = Servo 1 port, 13 = Servo 2 port
MIN_ANGLE = 0          # raise this / lower MAX_ANGLE to stay clear of your mechanism
MAX_ANGLE = 270

MIN_DUTY = 1638        # 0.5 ms pulse = 0 degrees     (same numbers as the course test)
MAX_DUTY = 8192        # 2.5 ms pulse = 270 degrees

servo = PWM(Pin(SERVO_PIN))
servo.freq(50)


def set_angle(angle):
    angle = max(MIN_ANGLE, min(MAX_ANGLE, angle))
    servo.duty_u16(int(MIN_DUTY + angle / 270 * (MAX_DUTY - MIN_DUTY)))
    print("at", angle, "degrees")


set_angle(135)
while True:
    text = input("Angle 0-270 (or sweep): ").strip().lower()
    if text == "sweep":
        for a in (0, 135, 270, 135, 0):
            set_angle(a)
            sleep_ms(1500)
    else:
        try:
            set_angle(float(text))
        except ValueError:
            print("Type a number from 0 to 270, or sweep")