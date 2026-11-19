# arya_ir_test.py
# IR receiver (TSOP4838) test. Prints 4 times a second whether it sees IR.
# Stop with Thonny's Stop.
#
# Wiring (bump/lens facing you, legs down, left to right 1, 2, 3):
#   leg 1 OUT -> GP14 (pin 19)     leg 2 GND -> GND     leg 3 VS -> 3V3
#
# How it works:
#   - the sensor's output is 1 when it sees no IR signal
#   - the output is 0 while it sees an IR signal (38 kHz, e.g. a TV remote
#     or the traffic light)
#   - every quarter of a second the code reads the pin over and over
#   - "pulses"  = how many times the output dropped from 1 to 0 in that time
#   - "low for" = how long in total the output stayed at 0 in that time
#   - if the output was 0 at any point, it prints "IR DETECTED",	
#     otherwise it prints "no IR"

from machine import Pin
from utime import ticks_ms, ticks_us, ticks_diff

IR_PIN = 14

ir = Pin(IR_PIN, Pin.IN, Pin.PULL_UP)

while True:
    start = ticks_ms()
    pulses = 0          # number of times the output dropped LOW
    low_us = 0          # total time spent LOW in this window
    last = ir.value()
    t_last = ticks_us()
    while ticks_diff(ticks_ms(), start) < 250:
        v = ir.value()
        now = ticks_us()
        if last == 0:
            low_us += ticks_diff(now, t_last)
        if v == 0 and last == 1:
            pulses += 1
        last = v
        t_last = now
    if pulses or low_us:
        print("IR DETECTED   pulses: %3d   low for %3d ms" % (pulses, low_us // 1000))
    else:
        print("no IR")