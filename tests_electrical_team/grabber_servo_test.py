# arya_servo_feedback_test.py
# Drives the 4-wire DSS-M15S servo and reads its real angle from the 4th wire.
#
# Wiring:
#   3-pin plug  -> PicoBot "Servo 1" port (GP15), battery on
#   4th wire (feedback) -> GP26 (header pin 31)
#
# On start it calibrates: it steps from 0 to 270 degrees in 10 steps, waits at
# each until the reading is steady, and records the feedback voltage. Keep the
# horn free to turn (about 15 seconds). Then type an angle (0 to 270) in the
# Thonny shell and press Enter. Stop with Thonny's Stop.

from machine import Pin, PWM, ADC
from utime import sleep_ms

SERVO_PIN = 15         # 15 = Servo 1 port, 13 = Servo 2 port
FEEDBACK_PIN = 26      # must be an analogue pin: 26, 27 or 28
CAL_STEPS = 10         # number of calibration steps between 0 and 270 degrees
MIN_DUTY = 1638        # 0.5 ms pulse = 0 degrees     (same numbers as the course test)
MAX_DUTY = 8192        # 2.5 ms pulse = 270 degrees

servo = PWM(Pin(SERVO_PIN))
servo.freq(50)
adc = ADC(Pin(FEEDBACK_PIN))


def set_angle(angle):
    angle = max(0, min(270, angle))
    servo.duty_u16(int(MIN_DUTY + angle / 270 * (MAX_DUTY - MIN_DUTY)))


def read_volts(samples=200):
    total = 0
    for _ in range(samples):            # average to cut noise
        total += adc.read_u16()
    return total / samples * 3.3 / 65535


def settled_volts():
    # wait until two readings 200 ms apart agree to 3 mV, then take a long average
    last = read_volts()
    for _ in range(25):
        sleep_ms(200)
        v = read_volts()
        if abs(v - last) < 0.003:
            break
        last = v
    return read_volts(2000)


# --- calibration table: (angle, volts) pairs ---
print("Calibrating - keep the horn free to turn")
set_angle(0)
sleep_ms(1500)
table = []
for i in range(CAL_STEPS + 1):
    a = 270 * i / CAL_STEPS
    set_angle(a)
    v = settled_volts()
    table.append((a, v))
    print("  %5.1f degrees -> %.4f V" % (a, v))

rising = table[-1][1] > table[0][1]
if abs(table[-1][1] - table[0][1]) < 0.3:
    print("The feedback voltage hardly changed - check the 4th wire is on GP%d" % FEEDBACK_PIN)

# how far the points are from one straight line (shows why a table is better)
worst = 0
for a, v in table:
    line = (v - table[0][1]) / (table[-1][1] - table[0][1] + 1e-9) * 270
    worst = max(worst, abs(line - a))
print("Biggest gap from a straight line: %.1f degrees" % worst)
print("CAL_TABLE =", [(round(a, 1), round(v, 4)) for a, v in table])


def volts_to_angle(v):
    # straight line between the two nearest calibration points
    for i in range(len(table) - 1):
        a0, v0 = table[i]
        a1, v1 = table[i + 1]
        lo, hi = (v0, v1) if rising else (v1, v0)
        last = i == len(table) - 2
        if (lo <= v <= hi) or (last and v1 != v0):
            if lo <= v <= hi or last:
                return a0 + (v - v0) / (v1 - v0) * (a1 - a0)
    return 0.0


def read_angle():
    v = read_volts()
    first, end = table[0][1], table[-1][1]
    if (rising and v <= first) or (not rising and v >= first):      # below 0 degrees
        a0, v0 = table[0]
        a1, v1 = table[1]
        return a0 + (v - v0) / (v1 - v0) * (a1 - a0)
    return volts_to_angle(v)


while True:
    text = input("Angle 0-270: ").strip()
    try:
        target = float(text)
    except ValueError:
        print("Type a number from 0 to 270")
        continue
    set_angle(target)
    for _ in range(8):                  # watch it arrive
        sleep_ms(250)
        print("  asked %5.1f   measured %5.1f degrees" % (target, read_angle()))