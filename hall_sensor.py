# hall_sensor.py
# Hall (magnetic) sensor code for the AGV - DRV5055 on GP28 (header pin 34).
#
# How it works:
#   - the sensor outputs a steady voltage with no magnet nearby
#   - one pole pushes the voltage up, the other pole pushes it down
#   - calibrate() measures the "no magnet" voltage (call it with no package near)
#   - read_mv() gives how far the voltage has moved from that, in millivolts
#   - polarity() turns that into "north", "south" or None (no magnet = blue box)
#
# Use in the robot code:
#   from hall_sensor import HallSensor
#   hall = HallSensor()          # once, at start-up, away from any package
#   ...
#   p = hall.polarity()          # "north", "south" or None
#
# Run this file on its own in Thonny to test: it prints the reading 4 times a second.

from machine import Pin, ADC
from utime import sleep_ms

HALL_PIN = 28          # GP28 = header pin 34 (must be an analogue pin: 26, 27 or 28)
THRESHOLD_MV = 50      # change needed to count as a magnet - tune this on the real boxes
SWAP_POLES = False     # set True if the sensor gets mounted the other way round
SAMPLES = 50           # readings averaged each time (cuts noise, takes about 1 ms)


class HallSensor:
    def __init__(self, pin=HALL_PIN, threshold_mv=THRESHOLD_MV, swap_poles=SWAP_POLES):
        self.adc = ADC(Pin(pin))
        self.threshold_mv = threshold_mv
        self.swap_poles = swap_poles
        self.rest_mv = 1650
        self.calibrate()

    def _volts_mv(self, samples=SAMPLES):
        total = 0
        for _ in range(samples):
            total += self.adc.read_u16()
        return total / samples * 3300 / 65535

    def calibrate(self):
        # Measure the no-magnet level. Call only when no package is near the sensor.
        total = 0
        for _ in range(20):
            total += self._volts_mv()
            sleep_ms(10)
        self.rest_mv = total / 20
        return self.rest_mv

    def read_mv(self):
        # Change from the no-magnet level in millivolts (+ or -).
        diff = self._volts_mv() - self.rest_mv
        return -diff if self.swap_poles else diff

    def polarity(self):
        # Positive change = north, negative change = south,
        # None when there is no magnet (blue box / nothing there).
        diff = self.read_mv()
        if diff > self.threshold_mv:
            return "north"
        if diff < -self.threshold_mv:
            return "south"
        return None


if __name__ == "__main__":
    print("Keep magnets away...")
    hall = HallSensor()
    print("No-magnet level: %.0f mV" % hall.rest_mv)
    while True:
        print("change %+5.0f mV   %s" % (hall.read_mv(), hall.polarity()))
        sleep_ms(250)