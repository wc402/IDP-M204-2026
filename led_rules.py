# led_rules.py
# The three LEDs on the AGV (through the optocoupler board), linked to the magnetic sensor.
#
# How it works:
#   - yellow is on steady when the robot is stopped, and flashes when it is moving
#   - a Timer does the flashing in the background, so the robot code never waits for it
#   - the magnetic sensor is imported from hall_sensor.py
#   - north magnet -> red LED, south magnet -> green LED, no magnet -> both off
#
# Run this file in Thonny (F5). hall_sensor.py must be saved on the Pico too.

from machine import Pin, Timer
from utime import sleep_ms
from hall_sensor import HallSensor

RED_PIN = 10           # GP10 = header pin 14
YELLOW_PIN = 11        # GP11 = header pin 15
GREEN_PIN = 12         # GP12 = header pin 16
FLASH_HZ = 2           # yellow flashes per second - check the task handout for the required rate


class Leds:
    def __init__(self):
        self.red = Pin(RED_PIN, Pin.OUT, value=0)
        self.yellow = Pin(YELLOW_PIN, Pin.OUT, value=1)
        self.green = Pin(GREEN_PIN, Pin.OUT, value=0)
        self.timer = Timer()
        self.is_moving = False

    def moving(self, on):
        # True = yellow flashes, False = yellow on steady.
        if on == self.is_moving:
            return
        self.is_moving = on
        if on:
            self.timer.init(freq=FLASH_HZ * 2, mode=Timer.PERIODIC,
                            callback=lambda t: self.yellow.toggle())
        else:
            self.timer.deinit()
            self.yellow.value(1)

    def package(self, pole):
        # "north" = red package, "south" = green package, None = no magnet.
        self.red.value(1 if pole == "north" else 0)
        self.green.value(1 if pole == "south" else 0)

    def off(self):
        self.timer.deinit()
        self.is_moving = False
        self.red.value(0)
        self.yellow.value(0)
        self.green.value(0)


if __name__ == "__main__":
    leds = Leds()            # yellow comes on steady
    print("Keep magnets away...")
    hall = HallSensor()      # measures the no-magnet level

    robot_is_moving = False  # we can't tell yet - the motor code will set this later

    try:
        while True:
            # yellow LED: flash if moving, steady if not
            if robot_is_moving:
                leds.moving(True)
            else:
                leds.moving(False)

            # red / green LED: from the magnetic sensor
            pole = hall.polarity()
            leds.package(pole)

            print("change %+5.0f mV   %s" % (hall.read_mv(), pole))
            sleep_ms(250)
    finally:
        leds.off()