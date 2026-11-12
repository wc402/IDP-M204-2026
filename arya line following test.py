# line_follow_4.py
# Four line sensors + two motors.
#
# MODE = "check"  : test the wiring. Spins each wheel in turn, then prints the
#                   four sensor readings. Laptop plugged in, wheels off the table.
# MODE = "follow" : follow the line. Inner pair steers, outer pair spots junctions.
#
# No button: it starts as soon as you press Run (or at power-up if saved as main.py).
# PRINT must be False for battery runs - a print with no laptop reading it stalls the loop.

from machine import Pin, PWM
from utime import sleep, sleep_ms, ticks_ms, ticks_diff

# ---------------- settings ----------------
MODE = "follow"         # "check" or "follow"
PRINT = True           # follow mode only: True on the lyaptop, False on battery
START_DELAY_S = 0      # follow mode: seconds to wait before moving (0 = start instantly)

# Line sensors: 1 = white line, 0 = black
PIN_OUTER_LEFT = 28    # header pin 34
PIN_INNER_LEFT = 27    # header pin 32
PIN_INNER_RIGHT = 26   # header pin 31
PIN_OUTER_RIGHT = 22   # header pin 29 (header pin 29 is GP22, not GP25)

# Motors. If the check shows a wheel is wrong, change these - no need to re-plug.
SWAP_MOTORS = False    # True if "LEFT wheel" in the check spins the right-hand wheel
REVERSE_LEFT = False   # True if the left wheel runs backwards in the check
REVERSE_RIGHT = False  # True if the right wheel runs backwards in the check

BASE = 50              # straight-line speed, percent
SLOW = 30              # inside wheel when steering
FAST = 60              # outside wheel when steering
# ------------------------------------------


class Motor:
    def __init__(self, dirPin, PWMPin, reverse=False):
        self.mDir = Pin(dirPin, Pin.OUT)
        self.pwm = PWM(Pin(PWMPin))
        self.pwm.freq(1000)
        self.fwd = 1 if reverse else 0   # direction-pin value that means "forward"
        self.off()

    def off(self):
        self.pwm.duty_u16(0)
        self.mDir.value(0)

    def Forward(self, speed=100):
        self.mDir.value(self.fwd)
        self.pwm.duty_u16(int(65535 * speed / 100))

    def Reverse(self, speed=30):
        self.mDir.value(1 - self.fwd)
        self.pwm.duty_u16(int(65535 * speed / 100))


# (direction pin, speed pin) for each motor socket on the PicoBot
right_pins = (4, 5)
left_pins = (7, 6)
if SWAP_MOTORS:
    left_pins, right_pins = right_pins, left_pins

motorL = Motor(left_pins[0], left_pins[1], REVERSE_LEFT)
motorR = Motor(right_pins[0], right_pins[1], REVERSE_RIGHT)

outer_left = Pin(PIN_OUTER_LEFT, Pin.IN, Pin.PULL_DOWN)
inner_left = Pin(PIN_INNER_LEFT, Pin.IN, Pin.PULL_DOWN)
inner_right = Pin(PIN_INNER_RIGHT, Pin.IN, Pin.PULL_DOWN)
outer_right = Pin(PIN_OUTER_RIGHT, Pin.IN, Pin.PULL_DOWN)


def check():
    """Wiring test: each wheel forward in turn, then live sensor readings."""
    print("WIRING CHECK - wheels off the table")
    sleep(2)

    print("LEFT wheel should now turn FORWARDS")
    motorL.Forward(40)
    sleep(1.5)
    motorL.off()
    sleep(1)

    print("RIGHT wheel should now turn FORWARDS")
    motorR.Forward(40)
    sleep(1.5)
    motorR.off()
    sleep(1)

    print("Sensors: hold each one over the white line - it should read 1")
    print("OL IL IR OR   (outer left, inner left, inner right, outer right)")
    while True:
        print(outer_left.value(), "", inner_left.value(), "", inner_right.value(), "", outer_right.value())
        sleep(0.2)


def follow():
    """Follow the line. Counts junctions seen by the outer sensors."""
    if START_DELAY_S:
        sleep(START_DELAY_S)

    count = 0
    on_junction = False
    saw_left = False
    saw_right = False
    last_seen = ticks_ms()

    while True:
        ol = outer_left.value()
        il = inner_left.value()
        ir = inner_right.value()
        orr = outer_right.value()

        if ol or orr:          # a branch or crossing: don't steer, drive straight over it
            motorL.Forward(BASE)
            motorR.Forward(BASE)
        elif il == ir:         # centred: straight on
            motorL.Forward(BASE)
            motorR.Forward(BASE)
        elif il:               # line is to the left: steer left
            motorL.Forward(SLOW)
            motorR.Forward(FAST)
        else:                  # line is to the right: steer right
            motorL.Forward(FAST)
            motorR.Forward(SLOW)

        # Junction counting: starts when an outer sensor sees white, ends once
        # both outer sensors have been back on black for 100 ms.
        now = ticks_ms()
        if ol or orr:
            if not on_junction:
                on_junction = True
                count += 1
                saw_left = False
                saw_right = False
            saw_left = saw_left or bool(ol)
            saw_right = saw_right or bool(orr)
            last_seen = now
        elif on_junction and ticks_diff(now, last_seen) > 100:
            on_junction = False
            if PRINT:
                if saw_left and saw_right:
                    side = "both sides"
                elif saw_left:
                    side = "left"
                else:
                    side = "right"
                print("Junction " + str(count) + ": " + side)

        sleep_ms(1)


if __name__ == "__main__":
    try:
        if MODE == "check":
            check()
        else:
            follow()
    finally:
        motorL.off()
        motorR.off()	