# arya_hall_test.py
# Prints the Hall (magnetic) sensor reading about 4 times a second.
# Stop with Thonny's Stop.
#
# Wiring (DRV5055, flat face towards you, legs down: left to right 1, 2, 3):
#   leg 1 VCC -> 3V3      leg 2 GND -> GND      leg 3 OUT -> GP28 (pin 34)
#
# Keep magnets away for the first second: it measures the "no magnet" level.

from machine import Pin, ADC
from utime import sleep_ms

HALL_PIN = 28          # must be an analogue pin: 26, 27 or 28
THRESHOLD_MV = 15      # how far from the no-magnet level counts as a magnet
SWAP_POLES = False     # set True if north and south come out the wrong way round

adc = ADC(Pin(HALL_PIN))


def read_volts():
    total = 0
    for _ in range(200):                # average 200 samples to cut noise
        total += adc.read_u16()
    return total / 200 * 3.3 / 65535


total = 0
for _ in range(20):
    total += read_volts()
    sleep_ms(50)
rest = total / 20
print("No-magnet level: %.2f V (should be about 1.65 V)" % rest)

while True:
    v = read_volts()
    diff = (v - rest) * 1000            # change in millivolts
    if SWAP_POLES:
        diff = -diff
    if diff > THRESHOLD_MV:
        pole = "SOUTH"
    elif diff < -THRESHOLD_MV:
        pole = "NORTH"
    else:
        pole = "no magnet"
    print("%.3f V   change %+5.0f mV   %s" % (v, (v - rest) * 1000, pole))
    sleep_ms(250)